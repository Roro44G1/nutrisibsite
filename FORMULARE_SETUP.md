# NutriSib – formulare locale (fără Jotform)

Fișiere:
- /programare.html – solicitare servicii, formularul Jotform 250983119555363
- /profil-wellness.html – profil wellness, formularul Jotform 242982957700365
- /nutrisib-forms.js – componente client
- /.netlify/functions/submit-nutrisib-form – gateway server → Google Sheets

## Configurare înainte de activare
1. Google Sheet privat cu filele exacte Programari și Wellness, antet A:P, partajat doar cu emailul contului de serviciu.
2. În Netlify, variabile SECRETE: NUTRISIB_SHEETS_ID, GOOGLE_SERVICE_ACCOUNT_EMAIL, GOOGLE_PRIVATE_KEY (cheie PEM; poate avea \n).
3. Nu introduce niciodată cheia în HTML, JavaScript client, git sau în ChatGPT.
4. Limite de trafic Netlify / CAPTCHA server-side și monitorizare; rate limiting în memorie este doar best-effort.
5. Revizuiește nota de informare GDPR: operator legal identificat, contact, scop, temei, durată de stocare, drepturi, împuterniciți, transferuri, mecanism de ștergere.
6. Nu activa colectarea datelor de sănătate fără verificarea bazei legale GDPR art. 9, control de acces, termene de retenție și evaluarea riscurilor.
7. Testează o solicitare fără date reale și verifică apariția rândului în tabul corect.
8. Redirecționează vechile CTA spre /programare.html numai după test complet.

## Diferențe față de Jotform
- Se păstrează principalele întrebări și opțiuni din PDF.
- Sexul și câteva opțiuni neprecizate de PDF au variante de interfață propuse, de confirmat.
- Profilul este reorganizat pentru completare condițională (medicamente, alergii, gustări, mic dejun).
- Acordurile promoționale/fotografii sunt opționale și separate.
- Nu se rezervă automat o dată/oră – cererea necesită confirmare.
- Consultația la distanță și profilul wellness sunt două fluxuri diferite.
- Nu se calculează automat IMC și nu se formulează un diagnostic.

## Atenție
Această implementare se află în staging, fără configurarea Google din această conversație.
Păstrați linkurile Jotform în producție până la integrarea complet funcțională.

## Stadiu validare
Publicarea rămâne blocată până la configurarea credențialelor, revizuirea consimțământului, controlul accesului și testarea înscrierii în Sheet. Ambele formulare solicită acord explicit pentru date privind sănătatea. Nu folosi date reale în testele inițiale.

## Schema exactă de coloane (A:T, ambele foi)
A Data primirii (UTC); B ID solicitare; C Tip formular; D Nume și prenume; E Sex; F Telefon; G E-mail; H Vârstă / data nașterii; I Serviciu / obiectiv; J Format preferat; K Acord date sănătate; L Marketing telefon; M Marketing e-mail; N Fotografii comunitate; O Fotografii social media; P Răspunsuri detaliate (JSON); Q Informare GDPR citită; R Versiune informare; S Status; T Observații interne.

Google Sheet FINAL ales: https://docs.google.com/spreadsheets/d/1LovZEFNwePFH9cyGg2pWMqYNv7l-rRVhuuUNSFmOv-s/edit
Identificator pentru variabila de mediu NUTRISIB_SHEETS_ID: 1LovZEFNwePFH9cyGg2pWMqYNv7l-rRVhuuUNSFmOv-s

VERIFICAT: Google Sheets API a creat filele `Programari` (gid=0) și `Wellness` (gid=6242026), fiecare cu 20 de antete pe A:T, rând 1 fixat, filtre și formatare. Nu există solicitări de utilizatori în registru.

IMPORTANT: succesul editării din contul ChatGPT NU autorizează Netlify să scrie. Urmează să configurăm serviciul Netlify prin `NUTRISIB_SHEETS_ID`, `GOOGLE_SERVICE_ACCOUNT_EMAIL`, `GOOGLE_PRIVATE_KEY` și să partajăm registrul NUMAI cu emailul Google al contului de serviciu, ca Editor. Nu partaja cheia PEM în conversație și nu transforma registrul în document public. Întâi test cu date fictive, apoi publicare.


## Activare controlată în Netlify (OBLIGATORIU)
1. În Google Cloud Console, configurează un **cont de serviciu dedicat** în proiectul tău și activează Google Sheets API.
2. În Google Sheet deja configurat, partajează fișierul cu adresa `client_email` a contului de serviciu ca **Editor**. Nu publica foaia pentru toată lumea.
3. În Netlify → Project configuration → Environment variables, adaugă cu scope **Functions** și context **Branch: construction**:
   - `NUTRISIB_SHEETS_ID` = `1LovZEFNwePFH9cyGg2pWMqYNv7l-rRVhuuUNSFmOv-s`
   - `GOOGLE_SERVICE_ACCOUNT_EMAIL` = adresa contului de serviciu
   - `GOOGLE_PRIVATE_KEY` = cheia privată PEM (secret; păstreaz-o doar în Netlify; folosește \n pentru liniile escapate)
   - `NUTRISIB_FORMS_ENABLED` = `true` **NUMAI DUPĂ** configurare și înaintea testului controlat.
4. Netlify necesită un **nou deploy** pentru aplicarea variabilelor runtime. Înainte de testare, verifică statusul GET `/.netlify/functions/submit-nutrisib-form`: `{"ready":true}`.
5. Testează cu date fictive trimise prin ambele formulare și verifică rândurile în taburile `Programari` și `Wellness`.
6. Dacă testul nu reușește, setează `NUTRISIB_FORMS_ENABLED=false`, re-deploy și investigează fără să introduci date reale.
7. Înainte de introducerea în producție, revizuiește informarea GDPR, scopurile, perioada de stocare și politica de acces la date de sănătate. Nu transfera cheia privată prin conversație.

Status actual: codul este pregătit pentru `construction`; nu există încă autorizarea Netlify și nu s-a realizat testul efectiv al scrierii.
