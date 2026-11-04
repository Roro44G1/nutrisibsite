// NutriSib – inițiere comandă magazin fizic (Herbalife sau LR – comenzi separate): validează coșul pe server,
// salvează comanda în Netlify Blobs și creează sesiunea Stripe Checkout.
import Stripe from "stripe";
import { getStore } from "@netlify/blobs";

// Catalogul (prețuri + VP) se citește de pe propriul site – sursa unică, generată de scripts/magazin_build.py.
let CACHE = null;
async function loadCatalog(origin) {
  if (CACHE && Date.now() - CACHE.t < 5 * 60 * 1000) return CACHE;
  const r = await fetch(`${origin}/magazin/catalog.json`);
  if (!r.ok) throw new Error(`catalog HTTP ${r.status}`);
  const d = await r.json();
  CACHE = { t: Date.now(), bySku: Object.fromEntries(d.produse.map((p) => [p.sku, p])), pk: Object.fromEntries((d.pachete || []).map((p) => [p.id, p])), prag: d.config.prag_vp, transport: d.config.transport,
    transportLR: d.config.lr?.transport ?? 25 };
  return CACHE;
}
const JSON_H = { "Content-Type": "application/json" };
const bad = (msg, status = 400) => new Response(JSON.stringify({ error: msg }), { status, headers: JSON_H });
const str = (v, max = 200) => (typeof v === "string" ? v.trim().slice(0, max) : "");
const num = (v, min, max) => { const n = Number(v); return Number.isFinite(n) && n >= min && n <= max ? n : null; };

export default async function handler(req) {
  if (req.method !== "POST") return bad("Metodă nepermisă", 405);
  let body;
  try { body = await req.json(); } catch { return bad("Cerere invalidă"); }

  // ---- produse (prețurile și VP-ul se iau DOAR din catalogul de pe server) ----
  const origin = new URL(req.url).origin;
  let cat;
  try { cat = await loadCatalog(origin); } catch (e) { console.error(e.message); return bad("Catalogul nu este disponibil momentan.", 503); }
  const BY_SKU = cat.bySku, PRAG_VP = cat.prag, TRANSPORT = cat.transport;
  const items = Array.isArray(body.items) ? body.items.slice(0, 40) : [];
  const lines = [];
  for (const it of items) {
    const key = String(it?.sku || "").toUpperCase();
    const q = Math.floor(Number(it?.qty));
    if (!(q >= 1 && q <= 99)) return bad("Coșul conține o cantitate invalidă. Reîncarcă pagina coșului.");
    if (key.includes(":")) {
      // pachet: "PK01:SKU,SKU,..." – fiecare SKU trebuie să fie o variantă permisă pentru unitatea respectivă
      const [id, list] = key.split(":"); const pk = cat.pk[id]; const skus = (list || "").split(",");
      if (!pk || skus.length !== pk.unitati.length || skus.some((s, i) => !pk.unitati[i].optiuni.includes(s) || !BY_SKU[s]))
        return bad("Coșul conține un pachet invalid. Reîncarcă pagina coșului.");
      if (skus.some((s) => BY_SKU[s].inactiv)) return bad(`Pachetul ${pk.nume} nu poate fi comandat încă. Elimină-l din coș pentru a continua.`);
      const comp = skus.map((s) => BY_SKU[s]);
      const separat = comp.reduce((a, c) => a + c.pret, 0);
      const t = Math.floor((separat * 95) / 100); let pret = Math.floor(t / 100) * 100 + 99; while (pret > t) pret -= 50;
      lines.push({ sku: key, cod: id, denumire: `Pachet ${pk.nume}`, varianta: comp.map((c) => `${c.denumire}${c.varianta ? " – " + c.varianta : ""}`).join("; "),
        pret, pret_separat: separat, vp: Math.round(comp.reduce((a, c) => a + c.vp, 0) * 100) / 100, qty: q, img: pk.img_mic, magazin: "herbalife",
        componente: comp.map((c) => ({ sku: c.sku, denumire: c.denumire, varianta: c.varianta, pret: c.pret })) });
      continue;
    }
    const p = BY_SKU[key];
    if (!p) return bad("Coșul conține un produs invalid. Reîncarcă pagina coșului.");
    if (p.inactiv) return bad(`Produsul ${p.denumire} nu poate fi comandat încă. Elimină-l din coș pentru a continua.`);
    lines.push({ sku: p.sku, denumire: p.denumire, varianta: p.varianta, pret: p.pret, vp: p.vp, qty: q, img: p.img_mic, magazin: p.magazin });
  }
  if (!lines.length) return bad("Coșul este gol.");
  // Sume în bani (întregi): prețurile LR au zecimale (ex. 171,79 lei).
  const subtotal = lines.reduce((s, l) => s + Math.round(l.pret * 100) * l.qty, 0) / 100;
  const vpTotal = Math.round(lines.reduce((s, l) => s + l.vp * l.qty, 0) * 100) / 100;
  // Coșuri și comenzi separate: o comandă conține produse dintr-un singur magazin (fiecare are coșul lui pe site).
  const magazine = [...new Set(lines.map((l) => l.magazin || "herbalife"))];
  if (magazine.length > 1) return bad("Produsele LR și Herbalife se comandă separat, fiecare din coșul magazinului său. Reîncarcă pagina coșului.");
  const magazin = magazine[0];
  // Transport: LR are tarif fix pe comandă; Herbalife e gratuit de la PRAG_VP.
  const transport = magazin === "lr" ? cat.transportLR : vpTotal >= PRAG_VP ? 0 : TRANSPORT;

  // ---- date client ----
  const c = body.client || {};
  const client = {
    nume: str(c.nume, 80), prenume: str(c.prenume, 80), email: str(c.email, 120).toLowerCase(), telefon: str(c.telefon, 20),
    judet: str(c.judet, 40), localitate: str(c.localitate, 80), adresa: str(c.adresa, 200), cod_postal: str(c.cod_postal, 6),
    observatii: str(c.observatii, 400),
  };
  for (const k of ["nume", "prenume", "email", "telefon", "judet", "localitate", "adresa"]) if (!client[k]) return bad("Completează toate câmpurile obligatorii de livrare.");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(client.email)) return bad("Adresa de e-mail nu este validă.");
  if (!/^[0-9+ ]{10,15}$/.test(client.telefon)) return bad("Numărul de telefon nu este valid.");
  if (c.accept_termeni !== true) return bad("Este necesară acceptarea Termenilor și condițiilor.");

  // CNP opțional (persoană fizică): validare format + cifră de control; dacă lipsește, factura se emite fără CNP.
  let cnp = null;
  if (c.pe_firma !== true && str(c.cnp, 13)) {
    cnp = str(c.cnp, 13);
    const k = "279146358279"; let sum = 0;
    for (let i = 0; i < 12; i++) sum += Number(cnp[i]) * Number(k[i]);
    const ctrl = sum % 11 === 10 ? 1 : sum % 11;
    if (!/^[1-9]\d{12}$/.test(cnp) || ctrl !== Number(cnp[12])) return bad("CNP-ul introdus nu este valid. Corectează-l sau lasă câmpul gol.");
  }

  // Client conectat (opțional): verificăm tokenul Supabase pe server și legăm comanda de cont.
  let userId = null;
  const auth = req.headers.get("authorization") || "";
  if (auth.startsWith("Bearer ") && process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY) {
    try {
      const u = await fetch(`${process.env.SUPABASE_URL}/auth/v1/user`, { headers: { apikey: process.env.SUPABASE_SERVICE_ROLE_KEY, Authorization: auth } });
      if (u.ok) userId = (await u.json()).id || null;
    } catch (e) { console.warn("Verificare token Supabase eșuată:", e.message); }
  }

  let firma = null;
  if (c.pe_firma === true) {
    firma = { denumire: str(c.firma_denumire, 150), cui: str(c.firma_cui, 20).toUpperCase(), regcom: str(c.firma_regcom, 30), adresa: str(c.firma_adresa, 200) };
    if (!firma.denumire || !firma.cui || !firma.adresa) return bad("Completează datele firmei pentru facturare.");
  }

  let profil = null;
  if (c.consimtamant_profil === true) {
    const yr = new Date().getFullYear();
    profil = {
      greutate_actuala: num(c.greutate_actuala, 30, 300), greutate_dorita: num(c.greutate_dorita, 30, 300), inaltime: num(c.inaltime, 100, 230),
      an_nastere: num(c.an_nastere, yr - 100, yr - 18), sex: ["Feminin", "Masculin"].includes(c.sex) ? c.sex : null,
      consimtamant: new Date().toISOString(),
    };
    if (profil.an_nastere) profil.varsta = yr - profil.an_nastere;
  }

  // ---- salvare comandă ----
  const now = new Date();
  const id = `NS-${now.toISOString().slice(2, 10).replace(/-/g, "")}-${Math.random().toString(36).slice(2, 6).toUpperCase()}`;
  const order = {
    id, creata: now.toISOString(), status: "in_asteptarea_platii", magazin,
    produse: lines, subtotal, transport, total: Math.round((subtotal + transport) * 100) / 100, vp_total: vpTotal,
    client, firma, cnp, user_id: userId, profil, termeni_acceptati: now.toISOString(),
  };
  const store = getStore({ name: "magazin-comenzi", consistency: "strong" });
  await store.setJSON(id, order);

  // ---- Stripe Checkout ----
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  try {
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      locale: "ro",
      currency: "ron",
      customer_email: client.email,
      client_reference_id: id,
      line_items: lines.map((l) => ({
        quantity: l.qty,
        price_data: {
          currency: "ron",
          unit_amount: Math.round(l.pret * 100),
          product_data: { name: `${l.denumire}${l.varianta ? " – " + l.varianta : ""}`.slice(0, 250), metadata: { sku: l.sku.slice(0, 450) } },
        },
      })),
      shipping_options: [{
        shipping_rate_data: {
          type: "fixed_amount",
          fixed_amount: { amount: Math.round(transport * 100), currency: "ron" },
          display_name: transport ? "Livrare prin curier" : `Livrare gratuită prin curier (${vpTotal} VP)`,
        },
      }],
      metadata: { magazin, order_id: id, vp_total: String(vpTotal) },
      payment_intent_data: { description: `Comanda NutriSib ${id}`, metadata: { magazin, order_id: id } },
      success_url: `${origin}/magazin/comanda-confirmata/?session_id={CHECKOUT_SESSION_ID}${magazin === "lr" ? "&magazin=lr" : ""}`,
      cancel_url: `${origin}${magazin === "lr" ? "/magazin/lr/cos/" : "/magazin/cos/"}`,
    });
    order.stripe_session = session.id;
    await store.setJSON(id, order);
    return new Response(JSON.stringify({ url: session.url, id }), { status: 200, headers: JSON_H });
  } catch (err) {
    console.error("Stripe checkout error:", err.message);
    return bad("Plata nu a putut fi inițiată. Încearcă din nou în câteva minute.", 502);
  }
}

export const config = { path: "/.netlify/functions/magazin-checkout" };
