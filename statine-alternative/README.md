# Alternative Naturale la Statine

Un site web informativ și profesional despre alternative naturale la statine pentru controlul colesterolului.

## Descriere

Site-ul prezintă un ghid complet bazat pe dovezi științifice despre:
- Modificări ale stilului de viață pentru gestionarea colesterolului
- 5 suplimente naturale cu potențial terapeutic (Orezul roșu fermentat, Berberina, Steroli vegetali, Fibre solubile, Omega-3)
- Informații detaliate despre eficacitate, dozaj și efecte secundare
- Considerații importante și disclaimer medical

## Design

**Filosofie de Design:** Organic Wellness Minimalism
- Palet de culori naturale: Verde salbatic (#7BA882), Crem cald (#F5F1E8), Terracotă (#D4845C)
- Tipografie elegantă: Playfair Display (titluri), Poppins (accente), Inter (corp)
- Layout asimetric cu imagini de înaltă calitate
- Design responsiv pentru toate dispozitivele

## Tehnologie

- **Framework:** React 19 + Vite
- **Styling:** Tailwind CSS 4 + shadcn/ui
- **Tipografie:** Google Fonts (Playfair Display, Poppins, Inter)
- **Imagini:** Imagini generate personalizat pentru secțiunile vizual prominente

## Instalare și Dezvoltare

```bash
# Instalare dependențe
pnpm install

# Pornire server de dezvoltare
pnpm dev

# Build pentru producție
pnpm build

# Preview build-ului
pnpm preview
```

## Structura Proiectului

```
statine-alternative/
├── client/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Home.tsx          # Pagina principală cu conținut complet
│   │   ├── components/           # Componente reutilizabile
│   │   ├── App.tsx               # Router și layout principal
│   │   ├── index.css             # Design tokens și stiluri globale
│   │   └── main.tsx              # Entry point React
│   ├── index.html                # HTML template
│   └── public/                   # Fișiere statice (favicon, robots.txt)
├── server/                       # Server Express (placeholder)
├── shared/                       # Tipuri și constante partajate
├── package.json                  # Dependențe și scripturi
├── vite.config.ts                # Configurare Vite
├── tsconfig.json                 # Configurare TypeScript
└── netlify.toml                  # Configurare Netlify
```

## Publicare pe Netlify

### Opțiunea 1: Conectare GitHub (Recomandat)

1. Mergeți la [Netlify](https://netlify.com)
2. Faceți click pe "New site from Git"
3. Selectați GitHub și autentificați-vă
4. Selectați repository-ul `nutrisibsite`
5. Configurați build settings:
   - **Build command:** `pnpm build`
   - **Publish directory:** `dist`
6. Faceți click pe "Deploy site"

### Opțiunea 2: Deploy Manual

```bash
# Instalare Netlify CLI
npm install -g netlify-cli

# Autentificare
netlify login

# Deploy
netlify deploy --prod --dir=dist
```

## Configurare pentru Blog Custom

### Integrare ca Subdomain

1. În Netlify, mergeți la "Site settings" → "Domain management"
2. Adăugați subdomain (ex: `statine.domeniul-vostru.com`)
3. Configurați DNS records conform instrucțiunilor Netlify

### Integrare ca Iframe în Blog

```html
<iframe 
  src="https://statine.domeniul-vostru.com" 
  width="100%" 
  height="800px" 
  frameborder="0"
  style="border: none; border-radius: 8px;">
</iframe>
```

### Integrare ca Link în Meniu Blog

Adăugați link-ul site-ului în meniul de navigare al blog-ului:
```html
<a href="https://statine.domeniul-vostru.com">Alternative Naturale la Statine</a>
```

## Variabile de Mediu

Creați fișier `.env.local` în rădăcina proiectului (dacă necesare):

```
VITE_API_URL=https://api.example.com
```

## Optimizare SEO

Site-ul include:
- Meta tags optimizate în `client/index.html`
- Titlu și descriere pentru social media
- Structură semantică HTML
- Imagini cu alt text descriptiv

## Licență

Conținut educativ. Consultați disclaimer-ul pe site pentru detalii legale.

## Contact și Suport

Pentru modificări sau întrebări, contactați echipa de dezvoltare.

---

**Creat cu ❤️ folosind Manus**
