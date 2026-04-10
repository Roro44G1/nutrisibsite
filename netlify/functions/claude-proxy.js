const SUPABASE_URL = "https://cwdbejilkbgdolywnozi.supabase.co";
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3ZGJlamlsa2JnZG9seXdub3ppIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU4MTUyMDIsImV4cCI6MjA5MTM5MTIwMn0.-HW2XAyYh9wkZde2zOpXQ9G-ogCLllfuB_sKzrO_h8I";

async function cautaInSupabase(intrebare) {
  try {
    // Cauta text simplu in Supabase (fara embeddings)
    const response = await fetch(
      `${SUPABASE_URL}/rest/v1/nutrisib_context?continut=ilike.*${encodeURIComponent(intrebare.substring(0, 50))}*&select=titlu,url,continut&limit=5`,
      {
        headers: {
          "apikey": SUPABASE_KEY,
          "Authorization": `Bearer ${SUPABASE_KEY}`
        }
      }
    );
    const data = await response.json();
    if (data && data.length > 0) {
      return data.map(r => `[${r.titlu} - ${r.url}]\n${r.continut}`).join("\n\n");
    }
    return "";
  } catch (e) {
    return "";
  }
}

exports.handler = async function(event) {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  try {
    const { messages } = JSON.parse(event.body);

    // Extrage ultima intrebare a utilizatorului
    const ultimaIntrebare = messages
      .filter(m => m.role === "user")
      .slice(-1)[0]?.content || "";

    // Cauta context relevant in Supabase
    const contextRelevant = await cautaInSupabase(ultimaIntrebare);

    const contextExtra = contextRelevant
      ? `\nINFORMATII RELEVANTE DIN SITE:\n${contextRelevant}\n`
      : "";

    const systemPrompt = `Ești Asistentul NutriSib, specialist în nutriție biologică și metoda C.E.L.O.S. creată de dr.ing. Radu Pascu din Sibiu, România.

CONTACT:
Email: nutrisib.club@gmail.com | Telefon: +40770276406 | Website: https://nutrisib.club

DESPRE NUTRISIB:
NutriSib oferă nutriție ultra-personalizată prin testare riguroasă. Filozofia este trecerea de la "cred că" la "știu că" — decizii bazate pe date biologice reale, nu pe diete generice. Radu Pascu a eliminat personal 50 kg folosind propria metodă. Locație: Sibiu, România.

METODA C.E.L.O.S.:
C — Calibrare: audit strategic, sarcina alostatică, KPI biologici definiți.
E — Energie: scanare BIA (Bioimpedanță Tanita), hardware biologic, eficiență energetică.
L — Longevitate: biorezonanță, software celular, entropia biologică.
OS — Optimizare Sistemică: dashboard biologic, arhitectura soluției, monitorizare KPI.

EVALUARE COMPLETĂ C.E.L.O.S. (~90 minute):
Sesiune de anamneză, scanare BIA completă, scanare biorezonanță, dashboard biologic, arhitectura soluției personalizate pe 4-6 luni. URL: https://nutrisib.club/#evaluare

CURS BIOHACKING 3.0:
Program de 6 săptămâni, 30 lecții video, 18+ ore HD. URL: https://nutrisib.club/biohack/
Module: 1) Mindset biohacking 3.0. 2) Self-tracking inteligent, HRV. 3) Biochimia alimentației, microbiom. 4) Arhitectura recuperării, somn. 5) Mișcare și longevitate. 6) Stres, cogniție, plan 90 zile.

BLOG: 80+ articole la https://nutrisib.club/blog — nutriție, sănătate, lifestyle, suplimente.
${contextExtra}
REGULI:
- Răspunde întotdeauna în română, indiferent de limba întrebării
- Fii prietenos, științific dar accesibil
- Dacă nu știi ceva specific, trimite la pagina relevantă sau sugerează contact direct
- Nu inventa prețuri specifice
- Pentru întrebări medicale, recomandă consultarea unui medic

REGULI STRICTE DE LIMBĂ ROMÂNĂ:
- Folosește diacritice corecte: ă, â, î, ș, ț
- Capitalizare românească: doar primul cuvânt al propoziției cu majusculă
- Nume proprii: NutriSib, C.E.L.O.S., Radu Pascu, Sibiu, Tanita
- Ton cald, profesionist, natural în română

FORMAT:
- Fără Markdown: fără asteriscuri, bold, liniuțe, hashtag-uri
- Propoziții și paragrafe naturale
- Maxim 3-4 paragrafe`;

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 1024,
        system: systemPrompt,
        messages: messages
      })
    });

    const data = await response.json();

    if (!data.content || !data.content[0]) {
      throw new Error("API error: " + JSON.stringify(data));
    }

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      },
      body: JSON.stringify({ response: data.content[0].text })
    };

  } catch (error) {
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Eroare server: " + error.message })
    };
  }
};
