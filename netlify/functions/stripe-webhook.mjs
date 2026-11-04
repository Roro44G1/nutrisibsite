import Stripe from "stripe";
import { getStore } from "@netlify/blobs";
import { Resend } from "resend";
import { PDFDocument, rgb } from "pdf-lib";
import fontkit from "@pdf-lib/fontkit";
import { handleMagazinOrder, trimiteEmail } from "../lib/magazin-comenzi.mjs";
import { smartbillActiv, emiteFacturaSB, descarcaFacturaSB, numeFisierFactura, taxaSB } from "../lib/smartbill.mjs";

// Adaugă aici un rând nou de fiecare dată când mai vinzi un produs nou.
// "price_XXXX" e Price ID-ul din Stripe (Products -> produsul tau -> sectiunea Pricing,
// NU id-ul Payment Link-ului).
// "blobKey" e numele exact sub care ai urcat fisierul in Netlify Blobs (pasul din README).
const PRODUCTS = {
  "price_1UDQjVRwvEzkBobC3syES2F0": {
    blobKey: "analize-medicale.pdf",
    fileName: "Analize Medicale fara Frica - NutriSib.pdf",
    title: "Analize Medicale fără Frică",
  },
  "price_1UDQTARwvEzkBobCDlpVBhGv": {
    blobKey: "BIOS_7_Zile_fara_zgomot.pdf",
    fileName: "BIOS Faza 1 - 7 Zile Fara Zgomot - NutriSib.pdf",
    title: "BIOS — Faza 1: 7 Zile Fără Zgomot",
  },
  "price_1UDQcXRwvEzkBobCUfLqkqPr": {
    blobKey: "BIOS_zero_crash.pdf",
    fileName: "BIOS Faza 2 - Zero Crash la 15.00 - NutriSib.pdf",
    title: "BIOS — Faza 2: Zero Crash la 15:00",
  },
  "price_1UDQdqRwvEzkBobC1qa7QdUc": {
    blobKey: "BIOS_zero_balonare.pdf",
    fileName: "BIOS Faza 3 - Zero Balonare dupa Masa - NutriSib.pdf",
    title: "BIOS — Faza 3: Zero Balonare după Masă",
  },
  "price_1UDQgpRwvEzkBobCeBMI47fx": {
    blobKey: "BIOS_zero_efect.pdf",
    fileName: "BIOS Faza 4 - Zero Efect Yo-Yo - NutriSib.pdf",
    title: "BIOS — Faza 4: Zero Efect Yo-Yo",
  },
};

const BLOB_STORE_NAME = "nutrisib-files";
// Starea fiecărei comenzi digitale (factură emisă, fișiere trimise), ca reîncercările Stripe să nu dubleze nimic.
const STARE_STORE_NAME = "comenzi-digitale";
// Evenimentele la care livrăm: plata confirmată imediat (card) sau confirmată ulterior (metode cu plată întârziată).
const EVENIMENTE_PLATA = new Set(["checkout.session.completed", "checkout.session.async_payment_succeeded"]);
const FONT_BLOB_KEY = "Inter-Regular.ttf";

export default async function handler(req) {
  if (req.method !== "POST") {
    return new Response("Method not allowed", { status: 405 });
  }

  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  const resend = new Resend(process.env.RESEND_API_KEY);

  const body = await req.text();
  const sig = req.headers.get("stripe-signature");

  let event;
  try {
    // constructEventAsync (nu constructEvent) -- necesar in acest runtime.
    event = await stripe.webhooks.constructEventAsync(
      body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );
  } catch (err) {
    console.error("Webhook signature error:", err.message);
    return new Response(`Webhook Error: ${err.message}`, { status: 400 });
  }

  if (!EVENIMENTE_PLATA.has(event.type)) {
    return new Response("OK", { status: 200 });
  }

  const session = event.data.object;

  // Comenzile din magazinul fizic (Herbalife etc.) au propriul flux.
  if (session.metadata?.magazin) {
    try {
      await handleMagazinOrder({ session, resend });
      return new Response("OK", { status: 200 });
    } catch (err) {
      console.error("Eroare comanda magazin:", err);
      return new Response("Internal error", { status: 500 });
    }
  }

  // Nu livrăm nimic până când plata nu e confirmată (la plățile întârziate vine ulterior
  // evenimentul checkout.session.async_payment_succeeded).
  if (!["paid", "no_payment_required"].includes(session.payment_status)) {
    console.log(`Plată neconfirmată încă (${session.payment_status}) pentru ${session.id}; aștept confirmarea.`);
    return new Response("OK", { status: 200 });
  }

  const customerEmail = session.customer_details?.email;
  const customerName = session.customer_details?.name || "Client NutriSib";

  if (!customerEmail) {
    console.error("Nu am gasit emailul cumparatorului in sesiunea Stripe.");
    return new Response("OK", { status: 200 });
  }

  // IMPORTANT: totul de mai jos ruleaza SINCRON (cu await), inainte de raspuns.
  // Netlify opreste executia imediat dupa ce trimite raspunsul catre Stripe --
  // orice procesare "in fundal" (fire-and-forget, fara await) ramane neterminata.
  // (Exact problema intalnita si la sistemul de pe radupascu.online.)
  try {
    const fullSession = await stripe.checkout.sessions.retrieve(session.id, {
      expand: ["line_items"],
    });

    // Procesăm (și facturăm) doar sesiunile care conțin produse digitale din lista PRODUCTS.
    // Alte plăți din același cont Stripe sunt ignorate aici, ca înainte.
    if (!fullSession.line_items.data.some((li) => PRODUCTS[li.price?.id])) {
      console.warn(`Sesiune fără produse digitale cunoscute, ignorată: ${session.id}`);
      return new Response("OK", { status: 200 });
    }

    const store = getStore(BLOB_STORE_NAME);
    const stareStore = getStore({ name: STARE_STORE_NAME, consistency: "strong" });
    const stare = (await stareStore.get(session.id, { type: "json" })) || { creata: new Date().toISOString(), trimise: [] };
    if (stare.procesata) {
      console.log(`Comanda digitală ${session.id} e deja procesată.`);
      return new Response("OK", { status: 200 });
    }
    const salveazaStare = () => stareStore.setJSON(session.id, stare);
    const orderId = session.id.slice(-8).toUpperCase();
    const date = new Date().toLocaleDateString("ro-RO");

    // ---- factură SmartBill (o singură dată pe comandă; erorile nu opresc livrarea fișierelor) ----
    if (!stare.factura && smartbillActiv() && (fullSession.amount_total || 0) > 0) {
      const lacat = await stareStore.setJSON(`lacat-factura/${session.id}`, { t: new Date().toISOString() }, { onlyIfNew: true });
      if (lacat.modified) {
        try {
          stare.factura = await facturaDigitala(fullSession, orderId);
          await salveazaStare();
        } catch (e) {
          console.error("SmartBill (produs digital):", e.message);
          await stareStore.delete(`lacat-factura/${session.id}`).catch(() => {});
          await alertaFactura(resend, fullSession, orderId, e.message).catch((err) => console.error("Alertă factură:", err.message));
        }
      } else {
        const recitita = await stareStore.get(session.id, { type: "json" });
        if (recitita?.factura) stare.factura = recitita.factura;
      }
    }
    let facturaPdf = null;
    if (stare.factura && !stare.factura_trimisa) {
      facturaPdf = await descarcaFacturaSB(stare.factura).catch((e) => { console.error("PDF factură:", e.message); return null; });
    }

    for (const item of fullSession.line_items.data) {
      const product = PRODUCTS[item.price.id];
      if (!product) {
        console.warn(`Price ID necunoscut in PRODUCTS, ignorat: ${item.price.id}`);
        continue;
      }
      if (stare.trimise.includes(item.price.id)) continue; // trimis deja la o încercare anterioară

      const masterBuffer = await store.get(product.blobKey, { type: "arrayBuffer" });
      if (!masterBuffer) {
        console.error(`Fisier lipsa in Netlify Blobs (store "${BLOB_STORE_NAME}"): ${product.blobKey}`);
        continue;
      }

      const stamped = await stampPdf(store, masterBuffer, {
        name: customerName,
        email: customerEmail,
        orderId,
        date,
      });

      // Factura se atașează la primul e-mail trimis.
      const cuFactura = Boolean(facturaPdf && !stare.factura_trimisa);
      const attachments = [
        {
          filename: product.fileName,
          content: Buffer.from(stamped).toString("base64"),
        },
      ];
      if (cuFactura) attachments.push({ filename: numeFisierFactura(stare.factura), content: facturaPdf.toString("base64") });

      await trimiteEmail(resend, {
        from: process.env.FROM_EMAIL || "NutriSib <comenzi@nutrisib.club>",
        to: customerEmail,
        subject: `Comanda ta NutriSib -- ${product.title}`,
        html: `
          <p>Bună${customerName ? `, ${customerName}` : ""}!</p>
          <p>Mulțumim pentru achiziția <strong>${product.title}</strong>. Găsești fișierul
          atașat mai jos — e personalizat cu numele tău, pentru uz personal.</p>
          ${cuFactura ? `<p>Tot aici găsești atașată și factura <strong>${stare.factura.serie} ${stare.factura.numar}</strong>.</p>` : ""}
          <p>Spor la citit,<br/>Echipa NutriSib</p>
        `,
        attachments,
      });

      stare.trimise.push(item.price.id);
      if (cuFactura) stare.factura_trimisa = new Date().toISOString();
      await salveazaStare();
      console.log(`Trimis "${product.title}" catre ${customerEmail} (comanda ${orderId})`);
    }

    stare.procesata = new Date().toISOString();
    await salveazaStare();
    return new Response("OK", { status: 200 });
  } catch (err) {
    console.error("Eroare procesare comanda:", err);
    return new Response("Internal error", { status: 500 });
  }
}

// ---- factura pentru produsele digitale: datele vin din pagina de plată Stripe ----
const rotunjit = (n) => Math.round(n * 100) / 100;
function facturaDigitala(s, orderId) {
  const cd = s.customer_details || {};
  const a = cd.address || {};
  const taxId = (cd.tax_ids || []).find((t) => t?.value);
  let tara = "Romania";
  if (a.country && a.country !== "RO") {
    try { tara = new Intl.DisplayNames(["en"], { type: "region" }).of(a.country) || a.country; } catch { tara = a.country; }
  }
  const adresa = { address: [a.line1, a.line2].filter(Boolean).join(", "), city: a.city || "", county: a.state || "", country: tara };
  const client = taxId
    ? { name: cd.business_name || cd.name || cd.email, vatCode: String(taxId.value).toUpperCase(), isTaxPayer: /^RO/i.test(taxId.value), ...adresa, email: cd.email }
    : { name: cd.name || cd.email, vatCode: "0000000000000", isTaxPayer: false, ...adresa, email: cd.email };
  const moneda = (s.currency || "ron").toUpperCase();
  const tax = taxaSB();
  const products = s.line_items.data.map((li) => ({
    name: li.description || "Produs digital NutriSib",
    isDiscount: false, measuringUnitName: "buc", currency: moneda,
    quantity: li.quantity || 1, price: rotunjit((li.amount_total || 0) / 100 / (li.quantity || 1)),
    isTaxIncluded: true, saveToDb: false, isService: true, ...tax,
  }));
  const total = (s.amount_total || 0) / 100;
  const suma = rotunjit(products.reduce((x, p) => x + p.price * p.quantity, 0));
  if (suma !== rotunjit(total)) console.warn(`Factura digitală ${orderId}: suma liniilor (${suma}) diferă de totalul Stripe (${total}).`);
  return emiteFacturaSB({ client, products, mentions: `Comanda online ${orderId}`, total });
}

async function alertaFactura(resend, s, orderId, eroare) {
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m]));
  const produse = (s.line_items?.data || []).map((li) => `${li.quantity}x ${esc(li.description)}`).join(", ");
  await trimiteEmail(resend, {
    from: process.env.FROM_EMAIL || "NutriSib <comenzi@nutrisib.club>",
    to: process.env.MAGAZIN_NOTIFY_EMAIL || "nutrisib.club@gmail.com",
    subject: `⚠️ Factură neemisă – comanda digitală ${orderId}`,
    html: `<div style="font-family:Arial,sans-serif;color:#1f2937">
      <p>SmartBill nu a emis factura pentru comanda digitală <strong>${orderId}</strong>. Fișierele au fost trimise clientului; factura trebuie emisă manual.</p>
      <p><strong>Client:</strong> ${esc(s.customer_details?.name)} · ${esc(s.customer_details?.email)}<br>
      <strong>Produse:</strong> ${produse}<br>
      <strong>Total:</strong> ${((s.amount_total || 0) / 100).toLocaleString("ro-RO")} ${esc((s.currency || "").toUpperCase())}</p>
      <p style="color:#b91c1c"><strong>Eroare SmartBill:</strong> ${esc(eroare)}</p>
      <p style="font-size:12px;color:#6b7280">Stripe: ${esc(s.id)}</p></div>`,
  });
}

async function stampPdf(store, masterBuffer, { name, email, orderId, date }) {
  const fontBytes = await store.get(FONT_BLOB_KEY, { type: "arrayBuffer" });
  if (!fontBytes) {
    throw new Error(`Fontul "${FONT_BLOB_KEY}" nu e in Netlify Blobs -- vezi README pasul de upload font.`);
  }

  const pdfDoc = await PDFDocument.load(masterBuffer);
  pdfDoc.registerFontkit(fontkit);
  const font = await pdfDoc.embedFont(fontBytes, { subset: true });

  const label = `Copie personală \u2014 ${name} \u00b7 ${email} \u00b7 comanda ${orderId} \u00b7 ${date}`;

  for (const page of pdfDoc.getPages()) {
    page.drawText(label, {
      x: 18,
      y: 10,
      size: 6.5,
      font,
      color: rgb(0.5, 0.5, 0.5),
      opacity: 0.55,
    });
  }

  return pdfDoc.save();
}

export const config = {
  path: "/.netlify/functions/stripe-webhook",
};
