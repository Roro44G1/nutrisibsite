// Generează magazin/oferta/oferta-nutrisib-herbalife.pdf din pagina /magazin/oferta/ (linkuri clicabile).
// Necesită: npm i -D playwright && npx playwright install chromium
// Rulare din rădăcina repo-ului, după scripts/magazin_build.py:  node scripts/oferta_pdf.mjs
import { chromium } from "playwright";
import { createServer } from "http";
import { readFile } from "fs/promises";
import { extname, join } from "path";
const TYPES = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".webp": "image/webp", ".png": "image/png", ".json": "application/json" };
const srv = createServer(async (req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname); if (p.endsWith("/")) p += "index.html";
  let buf; try { buf = await readFile(join(process.cwd(), p)); } catch { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "Content-Type": TYPES[extname(p)] || "application/octet-stream" }); res.end(buf);
}).listen(8799);
const b = await chromium.launch(); const pg = await b.newPage();
await pg.goto("http://localhost:8799/magazin/oferta/", { waitUntil: "load" });
await pg.emulateMedia({ media: "print" });
await pg.pdf({ path: "magazin/oferta/oferta-nutrisib-herbalife.pdf", format: "A4", printBackground: true,
  margin: { top: "12mm", bottom: "14mm", left: "10mm", right: "10mm" }, displayHeaderFooter: true, headerTemplate: "<span></span>",
  footerTemplate: '<div style="font-size:8px;width:100%;text-align:center;color:#666;font-family:Arial">NutriSib · Oferta Herbalife · nutrisib.club/magazin/oferta · pagina <span class="pageNumber"></span>/<span class="totalPages"></span></div>' });
await b.close(); srv.close(); console.log("PDF generat: magazin/oferta/oferta-nutrisib-herbalife.pdf");
