# NutriSib — webhook de personalizare PDF (varianta Netlify)

Acesta e exact tiparul care funcționează deja la radupascu.online (cartea AI Navigator 2026),
adaptat pentru PDF în loc de epub. Diferența tehnică: watermark-ul se scrie direct pe fiecare
pagină PDF (nu se injectează în HTML intern, cum se întâmplă la epub).

## Ce trebuie să ai deja, din Partea 1 (Payment Links)

Payment Link-urile create în Stripe pentru produsele din magazin — vezi Price ID-urile lor
în Stripe Dashboard → Products → (produsul) → Pricing.

---

## Pasul 1 — Instalează dependențele

În folderul local al proiectului (cel din care faci push pe GitHub pentru nutrisib.club):

```bash
npm install stripe @netlify/blobs resend pdf-lib @pdf-lib/fontkit
```

## Pasul 2 — Urcă fișierele "master" în Netlify Blobs (nu în GitHub)

La fel ca la epub — fișierele nu stau în repo, ca să nu fie publice.

```bash
netlify link
```
(dacă nu ai făcut deja legătura CLI-ului cu site-ul nutrisib.club)

Apoi, din folderul unde ai PDF-ul original:

```bash
netlify blobs:set nutrisib-files analize-medicale.pdf --input=./analize-medicale-master.pdf
```

Și fontul (o singură dată, e reutilizat pentru toate produsele):

```bash
netlify blobs:set nutrisib-files Inter-Regular.ttf --input=./Inter-Regular.ttf
```

Verifică că a urcat corect:

```bash
netlify blobs:get nutrisib-files analize-medicale.pdf --output=./test-download.pdf
```

Dacă `test-download.pdf` se deschide normal — e bine, poți șterge fișierul de test.

## Pasul 3 — Pune funcția în proiect

Copiază `netlify/functions/stripe-webhook.mjs` din acest pachet exact la aceeași cale
în proiectul tău local.

Deschide fișierul și înlocuiește în obiectul `PRODUCTS`:
- `price_XXXXXXXXXXXXXXXX` cu Price ID-ul real din Stripe
- `blobKey` cu numele exact folosit la `netlify blobs:set` (pasul 2)

**Când mai adaugi un produs nou pe viitor**, tot ce faci e: urci PDF-ul nou în Blobs
(pasul 2, cu alt nume) și adaugi un rând nou în `PRODUCTS` — exact ca la carte.

## Pasul 4 — Variabilele de mediu în Netlify

Netlify Dashboard → site-ul nutrisib.club → Site configuration → Environment variables.
Completezi valorile din `.env.example`:

- `STRIPE_SECRET_KEY` — Stripe Dashboard → Developers → API keys
- `STRIPE_WEBHOOK_SECRET` — îl iei la Pasul 5, de mai jos
- `RESEND_API_KEY` — din contul tău Resend existent (cel de la radupascu.online)
- `FROM_EMAIL` — ex. `NutriSib <comenzi@nutrisib.club>`

Bifează **"Contains secret values"** pentru primele trei.

## Pasul 5 — Domeniul nutrisib.club în Resend

Poți folosi **același cont Resend** de la carte — doar adaugi al doilea domeniu:
Resend Dashboard → Domains → Add Domain → `nutrisib.club` → adaugi înregistrările DNS
în Netlify (Domain management → DNS settings), la fel cum ai făcut pentru radupascu.online.

## Pasul 6 — Webhook-ul în Stripe

1. Stripe Dashboard → Developers → Webhooks → Add endpoint (sau, dacă vezi ecranul nou,
   **+ Add destination**)
2. Endpoint URL:
   ```
   https://nutrisib.club/.netlify/functions/stripe-webhook
   ```
3. Events: doar **`checkout.session.completed`**
4. Creezi endpoint-ul → click pe el → copiezi **Signing secret** (`whsec_...`)
5. Îl pui în Netlify ca `STRIPE_WEBHOOK_SECRET` (Pasul 4)

## Pasul 7 — Push și deploy

```bash
git add .
git commit -m "adauga webhook personalizare PDF"
git push
```

## Pasul 8 — Testează în siguranță, fără bani reali

1. Stripe Dashboard → activezi **Test mode** (sau accesezi direct `dashboard.stripe.com/test/payment-links`)
2. Creezi un Payment Link de test pentru produsul tău (preț 1 leu e suficient)
3. Deschizi linkul, plătești cu cardul de test: `4242 4242 4242 4242`, orice dată viitoare, orice CVC
4. Verifici: Netlify Dashboard → Functions → `stripe-webhook` → Logs
   Ar trebui să vezi `Trimis "Analize Medicale fără Frică" catre ...`
5. Verifici inbox-ul — ar trebui să vină emailul cu PDF-ul atașat, watermark-uit

## Dacă vin emailuri duplicate

Nu complica cu deduplicare în cod (am încercat asta la carte, nu a fost suficient de rapidă).
Fix-ul care chiar a funcționat: Stripe Dashboard → webhook-ul tău → **dezactivează retrimiterea
automată** dacă tot vezi dubluri după teste repetate.

## Ce NU rezolvă acest sistem

Nu e DRM — cineva tot poate redistribui fișierul primit. Ce face realist e să descurajeze
distribuirea casual (fiecare copie e vizibil „semnată") și să-ți dea un jurnal clar — cine a
primit exact ce fișier, când.
