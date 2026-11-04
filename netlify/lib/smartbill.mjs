// NutriSib – emiterea facturilor prin API-ul SmartBill (abonament Platinum).
// Folosit de ambele fluxuri: magazinul fizic (magazin-comenzi.mjs) și produsele digitale (stripe-webhook.mjs).
//
// Variabile de mediu Netlify:
//   SMARTBILL_USER   – e-mailul cu care intri în SmartBill
//   SMARTBILL_TOKEN  – tokenul din SmartBill: Contul meu > Integrări > API
//   SMARTBILL_CIF    – 38416337
//   SMARTBILL_SERIES – seria de facturi folosită pentru vânzările online
//   SMARTBILL_DRAFT  – opțional; "1" = facturile se salvează ca CIORNĂ (fără număr, fără e-Factura), pentru teste
//   SMARTBILL_TAX_NAME + SMARTBILL_TAX_PERCENT – doar dacă firma devine plătitoare de TVA
// Dacă lipsește una dintre primele patru, facturarea automată e sărită (comanda merge mai departe, factura se emite manual).

const SB = "https://ws.smartbill.ro/SBORO/api";
const auth = () => "Basic " + Buffer.from(`${process.env.SMARTBILL_USER}:${process.env.SMARTBILL_TOKEN}`).toString("base64");

export const smartbillActiv = () =>
  Boolean(process.env.SMARTBILL_USER && process.env.SMARTBILL_TOKEN && process.env.SMARTBILL_CIF && process.env.SMARTBILL_SERIES);
export const smartbillCiorna = () => process.env.SMARTBILL_DRAFT === "1";

// Cota de TVA se trimite doar dacă e configurată (II-ul nu este plătitor de TVA).
export const taxaSB = () =>
  process.env.SMARTBILL_TAX_NAME ? { taxName: process.env.SMARTBILL_TAX_NAME, taxPercentage: Number(process.env.SMARTBILL_TAX_PERCENT || 0) } : {};

// Unele răspunsuri SmartBill vin împachetate (ex. { sbcResponse: {...} }); le despachetăm dacă e cazul.
const despacheteaza = (j) => {
  if (j && typeof j === "object" && !Array.isArray(j)) {
    const k = Object.keys(j);
    if (k.length === 1 && j[k[0]] && typeof j[k[0]] === "object") return j[k[0]];
  }
  return j;
};

/**
 * Emite o factură încasată cu cardul.
 * @param {{ client: object, products: object[], mentions?: string, total: number }} f
 * @returns {Promise<{serie: string, numar: string, url: string|null, ciorna: boolean}|null>} null dacă SmartBill nu e configurat
 */
export async function emiteFacturaSB({ client, products, mentions, total }) {
  if (!smartbillActiv()) return null;
  const ciorna = smartbillCiorna();
  const body = {
    companyVatCode: process.env.SMARTBILL_CIF,
    seriesName: process.env.SMARTBILL_SERIES,
    issueDate: new Date().toISOString().slice(0, 10),
    isDraft: ciorna,
    client: { country: "Romania", saveToDb: false, ...client },
    products,
    mentions: mentions || "",
    // Încasarea se înregistrează odată cu factura; la o ciornă nu are sens.
    ...(ciorna ? {} : { payment: { value: Math.round(total * 100) / 100, type: "Card", isCash: false } }),
  };
  const r = await fetch(`${SB}/invoice`, {
    method: "POST",
    headers: { Authorization: auth(), "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  const j = despacheteaza(await r.json().catch(() => ({})));
  if (!r.ok || j?.errorText) throw new Error(j?.errorText || j?.message || `HTTP ${r.status}`);
  return { serie: j.series || process.env.SMARTBILL_SERIES, numar: j.number ? String(j.number) : "", url: j.url || null, ciorna };
}

/** Descarcă PDF-ul unei facturi emise (nu și al unei ciorne). */
export async function descarcaFacturaSB(f) {
  if (!f || f.ciorna || !f.numar) return null;
  const u = `${SB}/invoice/pdf?cif=${encodeURIComponent(process.env.SMARTBILL_CIF)}&seriesname=${encodeURIComponent(f.serie)}&number=${encodeURIComponent(f.numar)}`;
  const r = await fetch(u, { headers: { Authorization: auth(), Accept: "application/octet-stream" } });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return Buffer.from(await r.arrayBuffer());
}

export const numeFisierFactura = (f) => `Factura-${f.serie}${f.numar}.pdf`;
