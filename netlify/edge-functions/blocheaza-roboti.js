// Blochează roboții de colectare AI și extragere automată pe magazinele NutriSib (Herbalife, LR) și pe sursele lor.
// Motoarele de căutare (Googlebot, Bingbot…) și căutarea AI la cererea utilizatorului (OAI-SearchBot, ChatGPT-User,
// PerplexityBot, Perplexity-User, Claude-SearchBot, Claude-User) NU sunt în listă, deci au acces normal.
// Lista e sincronizată cu robots.txt; roboții care se dau drept browser obișnuit nu pot fi recunoscuți aici.
const BLOCAT = ["gptbot", "claudebot", "anthropic-ai", "ccbot", "google-extended", "googleother", "applebot-extended", "bytespider", "meta-externalagent", "meta-externalfetcher", "facebookbot", "amazonbot", "diffbot", "imagesiftbot", "omgilibot", "omgili", "petalbot", "timpibot", "cohere-ai", "cohere-training-data-crawler", "ai2bot", "ai2bot-dolma", "pangubot", "kangaroo bot", "webzio-extended", "youbot", "scrapy", "img2dataset", "velenpublicwebcrawler", "icc-crawler", "sidetrade indexer bot", "dataforseobot", "mj12bot", "semrushbot", "ahrefsbot", "dotbot", "blexbot", "python-requests", "python-urllib", "aiohttp", "httpx", "go-http-client", "node-fetch", "axios", "curl/", "wget", "httrack", "libwww-perl", "okhttp", "java/", "apache-httpclient", "headlesschrome", "phantomjs", "sitesucker", "teleport", "webcopier", "webzip", "offline explorer", "screaming frog"];

export default async (request, context) => {
  const ua = (request.headers.get("user-agent") || "").toLowerCase();
  if (BLOCAT.some((b) => ua.includes(b))) {
    return new Response("Acces refuzat: extragerea automată a conținutului nu este permisă (vezi /robots.txt și /magazin/termeni-si-conditii/).", {
      status: 403,
      headers: { "content-type": "text/plain; charset=utf-8", "x-robots-tag": "noindex", "cache-control": "no-store" },
    });
  }
  return context.next();
};

export const config = { path: ["/magazin/*", "/produse/*", "/scripts/*", "/sitemap-magazin.xml"] };
