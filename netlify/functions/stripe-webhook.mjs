import Stripe from "stripe";
import { getStore } from "@netlify/blobs";
import { Resend } from "resend";
import { PDFDocument, rgb } from "pdf-lib";
import fontkit from "@pdf-lib/fontkit";

// Adaugă aici un rând nou de fiecare dată când mai vinzi un produs nou.
// "price_XXXX" e Price ID-ul din Stripe (Products -> produsul tau -> sectiunea Pricing,
// NU id-ul Payment Link-ului).
// "blobKey" e numele exact sub care ai urcat fisierul in Netlify Blobs (pasul din README).
const PRODUCTS = {
  "price_XXXXXXXXXXXXXXXX": {
    blobKey: "analize-medicale.pdf",
    fileName: "Analize Medicale fara Frica - NutriSib.pdf",
    title: "Analize Medicale fără Frică",
  },
  // exemplu pentru cand adaugi si BIOS aici:
  // "price_YYYYYYYYYYYYYYYY": {
  //   blobKey: "bios-faza1.pdf",
  //   fileName: "BIOS Faza 1 - NutriSib.pdf",
  //   title: "BIOS — Faza 1: 7 Zile Fara Zgomot",
  // },
};

const BLOB_STORE_NAME = "nutrisib-files";
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

  if (event.type !== "checkout.session.completed") {
    return new Response("OK", { status: 200 });
  }

  const session = event.data.object;
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

    const store = getStore(BLOB_STORE_NAME);
    const orderId = session.id.slice(-8).toUpperCase();
    const date = new Date().toLocaleDateString("ro-RO");

    for (const item of fullSession.line_items.data) {
      const product = PRODUCTS[item.price.id];
      if (!product) {
        console.warn(`Price ID necunoscut in PRODUCTS, ignorat: ${item.price.id}`);
        continue;
      }

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

      await resend.emails.send({
        from: process.env.FROM_EMAIL || "NutriSib <comenzi@nutrisib.club>",
        to: customerEmail,
        subject: `Comanda ta NutriSib -- ${product.title}`,
        html: `
          <p>Bună${customerName ? `, ${customerName}` : ""}!</p>
          <p>Mulțumim pentru achiziția <strong>${product.title}</strong>. Găsești fișierul
          atașat mai jos — e personalizat cu numele tău, pentru uz personal.</p>
          <p>Spor la citit,<br/>Echipa NutriSib</p>
        `,
        attachments: [
          {
            filename: product.fileName,
            content: Buffer.from(stamped).toString("base64"),
          },
        ],
      });

      console.log(`Trimis "${product.title}" catre ${customerEmail} (comanda ${orderId})`);
    }

    return new Response("OK", { status: 200 });
  } catch (err) {
    console.error("Eroare procesare comanda:", err);
    return new Response("Internal error", { status: 500 });
  }
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
