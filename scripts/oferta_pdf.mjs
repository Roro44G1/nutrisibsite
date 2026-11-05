// Generează PDF-ul ofertei NutriSib din pagina ei (linkuri clicabile):
//   Herbalife: /magazin/oferta/     → magazin/oferta/oferta-nutrisib-herbalife.pdf   (node scripts/oferta_pdf.mjs, după magazin_build.py)
//   LR:        /magazin/lr/oferta/  → magazin/lr/oferta/oferta-nutrisib-lr.pdf      (node scripts/oferta_pdf.mjs lr, după magazin_lr.py)
// Necesită: npm i -D playwright && npx playwright install chromium
import { chromium } from "playwright";
import { createServer } from "http";
import { readFile } from "fs/promises";
import { extname, join } from "path";
const TYPES = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".webp": "image/webp", ".png": "image/png", ".json": "application/json", ".svg": "image/svg+xml" };
const OF = {
  herbalife: { pagina: "/magazin/oferta/", pdf: "magazin/oferta/oferta-nutrisib-herbalife.pdf", nume: "Herbalife", url: "nutrisib.club/magazin/oferta" },
  lr: { pagina: "/magazin/lr/oferta/", pdf: "magazin/lr/oferta/oferta-nutrisib-lr.pdf", nume: "LR", url: "nutrisib.club/magazin/lr/oferta" },
}[process.argv[2] || "herbalife"];
if (!OF) { console.error("Magazin necunoscut. Folosește: node scripts/oferta_pdf.mjs [herbalife|lr]"); process.exit(1); }
const srv = createServer(async (req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname); if (p.endsWith("/")) p += "index.html";
  let buf; try { buf = await readFile(join(process.cwd(), p)); } catch { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "Content-Type": TYPES[extname(p)] || "application/octet-stream" }); res.end(buf);
}).listen(8799);
const b = await chromium.launch(); const pg = await b.newPage();
await pg.goto(`http://localhost:8799${OF.pagina}`, { waitUntil: "load" });
await pg.emulateMedia({ media: "print" });
await pg.pdf({ path: OF.pdf, format: "A4", printBackground: true,
  margin: { top: "12mm", bottom: "14mm", left: "10mm", right: "10mm" }, displayHeaderFooter: true, headerTemplate: "<span></span>",
  footerTemplate: `<div style="font-size:8px;width:100%;text-align:center;color:#666;font-family:Arial">NutriSib · Oferta ${OF.nume} · ${OF.url} · pagina <span class="pageNumber"></span>/<span class="totalPages"></span></div>` });
await b.close(); srv.close(); console.log(`PDF generat: ${OF.pdf}`);
