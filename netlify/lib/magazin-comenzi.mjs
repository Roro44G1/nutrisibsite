// NutriSib – procesarea comenzilor din magazinul fizic după plata Stripe:
// marchează comanda plătită, emite factura în SmartBill (dacă e configurat),
// trimite e-mailurile (client + NutriSib) și, opțional, contactul în GHL.
import { getStore } from "@netlify/blobs";
import { smartbillActiv, emiteFacturaSB, descarcaFacturaSB, numeFisierFactura, taxaSB } from "./smartbill.mjs";

const lei = (n) => `${Number(n).toLocaleString("ro-RO")} lei`;
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));

export async function handleMagazinOrder({ session, resend }) {
  const orderId = session.metadata?.order_id;
  if (!orderId) { console.error("Sesiune magazin fără order_id", session.id); return; }
  const store = getStore({ name: "magazin-comenzi", consistency: "strong" });
  const order = await store.get(orderId, { type: "json" });
  if (!order) { console.error("Comanda nu există în Blobs:", orderId); return; }
  if (order.procesata) { console.log("Comanda deja procesată:", orderId); return; }
  // Comenzi plătite înainte de fluxul pe etape (fără câmpul `etape`): erau deja complet procesate.
  if (order.status === "platita" && !order.etape) { console.log("Comandă procesată de versiunea anterioară:", orderId); return; }
  if (session.payment_status !== "paid") { console.warn("Sesiune neplătită încă (se așteaptă confirmarea plății):", orderId, session.payment_status); return; }

  // Fiecare pas e marcat în comandă, ca o reîncercare Stripe să reia doar ce a rămas neterminat.
  const salveaza = () => store.setJSON(orderId, order);
  if (order.status !== "platita") {
    order.status = "platita";
    order.etape = 1;
    order.platita = new Date().toISOString();
    order.stripe = { session: session.id, payment_intent: session.payment_intent, suma: (session.amount_total || 0) / 100 };
    if (Math.round(order.stripe.suma * 100) !== Math.round(order.total * 100)) console.warn("Diferență total Stripe vs comandă", orderId, order.stripe.suma, order.total);
    await salveaza();
  }

  // ---- factură SmartBill (o singură dată pe comandă) ----
  let facturaPdf = null, facturaEroare = null;
  if (!order.factura && smartbillActiv()) {
    const lacat = await store.setJSON(`lacat-factura/${orderId}`, { t: new Date().toISOString() }, { onlyIfNew: true });
    if (lacat.modified) {
      try {
        order.factura = await emiteFactura(order);
        await salveaza();
      } catch (e) {
        facturaEroare = e.message; console.error("SmartBill:", e.message);
        await store.delete(`lacat-factura/${orderId}`).catch(() => {});
      }
    } else {
      // O altă livrare a aceluiași eveniment emite deja factura – citim comanda din nou.
      const recitita = await store.get(orderId, { type: "json" });
      if (recitita?.factura) order.factura = recitita.factura;
    }
  }
  const factura = order.factura || null;
  if (factura && !order.email_client) facturaPdf = await descarcaFacturaSB(factura).catch((e) => { console.error("PDF factură:", e.message); return null; });

  // ---- istoric în contul clientului (Supabase; fără CNP și fără profil nutrițional) ----
  await salveazaInSupabase(order).catch((e) => console.error("Supabase:", e.message));

  // ---- e-mailuri ----
  const from = process.env.FROM_EMAIL || "NutriSib <comenzi@nutrisib.club>";
  const notify = process.env.MAGAZIN_NOTIFY_EMAIL || "nutrisib.club@gmail.com";
  const tabel = tabelProduse(order);
  const adresa = `${esc(order.client.adresa)}, ${esc(order.client.localitate)}, jud. ${esc(order.client.judet)}${order.client.cod_postal ? ", " + esc(order.client.cod_postal) : ""}`;

  if (!order.email_client) {
  await trimiteEmail(resend, {
    from, to: order.client.email, reply_to: notify,
    subject: `Comanda ta NutriSib ${order.id} a fost confirmată`,
    html: `<div style="font-family:Arial,sans-serif;color:#1f2937;max-width:620px">
      <h2 style="color:#1B2A4A">Mulțumim, ${esc(order.client.prenume)}!</h2>
      <p>Am primit plata pentru comanda <strong>${order.id}</strong>. O pregătim pentru livrare și revenim cu detaliile de expediere.</p>
      ${tabel}
      <p><strong>Livrare la:</strong> ${esc(order.client.nume)} ${esc(order.client.prenume)}, ${adresa}, tel. ${esc(order.client.telefon)}</p>
      ${factura && !factura.ciorna ? `<p>Factura <strong>${esc(factura.serie)} ${esc(factura.numar)}</strong> ${facturaPdf ? "este atașată acestui e-mail" : "îți va fi trimisă separat"}.</p>` : `<p>Factura îți va fi trimisă separat, pe e-mail.</p>`}
      <p style="font-size:13px;color:#4b5563">Ai dreptul de retragere în 14 zile de la primire, pentru produsele nedesigilate – vezi <a href="https://nutrisib.club/magazin/retur/">condițiile de retur</a>. Pentru orice întrebare, răspunde la acest e-mail.</p>
      <p>Cu drag,<br>NutriSib</p></div>`,
    attachments: facturaPdf ? [{ filename: numeFisierFactura(factura), content: facturaPdf.toString("base64") }] : undefined,
  });
  order.email_client = new Date().toISOString(); await salveaza();
  }

  const firma = order.firma ? `<p><strong>Factură pe firmă:</strong> ${esc(order.firma.denumire)}, CUI ${esc(order.firma.cui)}${order.firma.regcom ? ", " + esc(order.firma.regcom) : ""}, ${esc(order.firma.adresa)}</p>` : "";
  const p = order.profil;
  const profil = p ? `<p><strong>Profil nutrițional (cu consimțământ, ${esc(p.consimtamant)}):</strong> greutate ${p.greutate_actuala ?? "–"} kg → ${p.greutate_dorita ?? "–"} kg, înălțime ${p.inaltime ?? "–"} cm, an naștere ${p.an_nastere ?? "–"}${p.varsta ? ` (${p.varsta} ani)` : ""}, sex ${esc(p.sex || "–")}</p>` : "";
  if (!order.email_nutrisib) {
  await trimiteEmail(resend, {
    from, to: notify, reply_to: order.client.email,
    subject: `🛒 Comandă nouă ${order.id} – ${lei(order.total)} (${order.vp_total} VP)`,
    html: `<div style="font-family:Arial,sans-serif;color:#1f2937">
      <h2>Comandă nouă ${order.id}</h2>${tabel}
      <p><strong>Client:</strong> ${esc(order.client.nume)} ${esc(order.client.prenume)} · ${esc(order.client.email)} · ${esc(order.client.telefon)}</p>
      <p><strong>Livrare:</strong> ${adresa}</p>
      ${order.client.observatii ? `<p><strong>Observații:</strong> ${esc(order.client.observatii)}</p>` : ""}
      ${firma}${profil}
      <p><strong>Factură:</strong> ${factura ? (factura.ciorna ? `<span style="color:#b45309">CIORNĂ în SmartBill (mod test SMARTBILL_DRAFT) – șterge-o sau emite-o manual</span>` : `${esc(factura.serie)} ${esc(factura.numar)}`) : facturaEroare ? `<span style="color:#b91c1c">NEEMISĂ – eroare SmartBill: ${esc(facturaEroare)}</span>` : smartbillActiv() ? "în curs de emitere de altă execuție – verifică în SmartBill" : "SmartBill neconfigurat – emite manual"}</p>
      <p style="font-size:12px;color:#6b7280">Stripe: ${esc(session.id)}</p></div>`,
  });
  order.email_nutrisib = new Date().toISOString(); await salveaza();
  }

  // ---- GHL (opțional; fără date de sănătate) ----
  if (process.env.GHL_WEBHOOK_URL && !order.ghl) {
    await fetch(process.env.GHL_WEBHOOK_URL, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: order.client.email, phone: order.client.telefon, firstName: order.client.prenume, lastName: order.client.nume,
        city: order.client.localitate, state: order.client.judet, source: "magazin-nutrisib", tags: ["client-herbalife"],
        order_id: order.id, total: order.total, vp: order.vp_total, produse: order.produse.map((l) => `${l.qty}x ${l.denumire} ${l.varianta}`).join("; ") }),
    }).then(() => { order.ghl = new Date().toISOString(); }).catch((e) => console.error("GHL:", e.message));
  }
  order.procesata = new Date().toISOString();
  await salveaza();
  console.log("Comandă magazin procesată:", order.id);
}

// Resend nu aruncă eroare la eșec (întoarce { error }); o transformăm în excepție ca Stripe să reîncerce.
export async function trimiteEmail(resend, payload) {
  const r = await resend.emails.send(payload);
  if (r?.error) throw new Error(`Resend: ${r.error.message || JSON.stringify(r.error)}`);
  return r?.data;
}

function tabelProduse(o) {
  const rows = o.produse.map((l) => `<tr><td style="padding:6px 8px;border-bottom:1px solid #e5e7eb">${esc(l.denumire)}${l.varianta ? `<br><small>${esc(l.varianta)} · cod ${esc(l.sku)}</small>` : ""}</td><td style="padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:center">${l.qty}</td><td style="padding:6px 8px;border-bottom:1px solid #e5e7eb;text-align:right">${lei(l.pret * l.qty)}</td></tr>`).join("");
  return `<table style="border-collapse:collapse;width:100%;font-size:14px">${rows}
    <tr><td colspan="2" style="padding:6px 8px;text-align:right">Transport</td><td style="padding:6px 8px;text-align:right">${o.transport ? lei(o.transport) : "gratuit"}</td></tr>
    <tr><td colspan="2" style="padding:6px 8px;text-align:right"><strong>Total</strong></td><td style="padding:6px 8px;text-align:right"><strong>${lei(o.total)}</strong></td></tr></table>`;
}

// ---------------- SmartBill (vezi ./smartbill.mjs) ----------------
function emiteFactura(o) {
  const tax = taxaSB();
  const client = o.firma
    ? { name: o.firma.denumire, vatCode: o.firma.cui, regCom: o.firma.regcom || "", address: o.firma.adresa, isTaxPayer: /^RO/i.test(o.firma.cui), city: o.client.localitate, county: o.client.judet, email: o.client.email }
    : { name: `${o.client.nume} ${o.client.prenume}`, vatCode: o.cnp || "0000000000000", address: o.client.adresa, isTaxPayer: false, city: o.client.localitate, county: o.client.judet, email: o.client.email };
  const products = o.produse.map((l) => ({ name: `${l.denumire}${l.varianta ? " - " + l.varianta : ""}`, code: l.sku, isDiscount: false, measuringUnitName: "buc",
    currency: "RON", quantity: l.qty, price: l.pret, isTaxIncluded: true, saveToDb: false, isService: false, ...tax }));
  if (o.transport) products.push({ name: "Transport", code: "TRANSPORT", isDiscount: false, measuringUnitName: "buc", currency: "RON", quantity: 1,
    price: o.transport, isTaxIncluded: true, saveToDb: false, isService: true, ...tax });
  return emiteFacturaSB({ client, products, mentions: `Comanda online ${o.id}`, total: o.total });
}

// ---------------- Supabase (istoric comenzi) ----------------
// Variabile de mediu: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY. Dacă lipsesc, pasul e sărit.
export async function salveazaInSupabase(o) {
  const { SUPABASE_URL: U, SUPABASE_SERVICE_ROLE_KEY: K } = process.env;
  if (!U || !K) return;
  const row = {
    id: o.id, user_id: o.user_id || null, email: o.client.email, status: o.status, creata: o.creata, platita: o.platita || null,
    produse: o.produse.map(({ sku, denumire, varianta, pret, vp, qty, componente }) => ({ sku, denumire, varianta, pret, vp, qty, ...(componente ? { componente } : {}) })),
    subtotal: o.subtotal, transport: o.transport, total: o.total, vp_total: o.vp_total,
    livrare: { nume: o.client.nume, prenume: o.client.prenume, telefon: o.client.telefon, judet: o.client.judet, localitate: o.client.localitate, adresa: o.client.adresa, cod_postal: o.client.cod_postal },
    firma: o.firma || null, factura: o.factura || null,
  };
  const r = await fetch(`${U}/rest/v1/magazin_comenzi?on_conflict=id`, {
    method: "POST",
    headers: { apikey: K, Authorization: `Bearer ${K}`, "Content-Type": "application/json", Prefer: "resolution=merge-duplicates,return=minimal" },
    body: JSON.stringify(row),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status} ${await r.text()}`);
}
