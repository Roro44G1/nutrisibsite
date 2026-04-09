const { SITE_CONTEXT } = require('./context_site');

exports.handler = async function(event) {
  if (event.httpMethod !== "POST") {
    return { statusCode: 405, body: "Method Not Allowed" };
  }

  try {
    const { messages } = JSON.parse(event.body);

    const systemPrompt = `Ești Asistentul NutriSib, specialist în nutriție biologică și metoda C.E.L.O.S. creată de dr.ing. Radu Pascu din Sibiu, România.

CONTACT NUTRISIB:
- Email: nutrisib.club@gmail.com
- Telefon: +40770276406
- Website: https://nutrisib.club

INFORMATII COMPLETE DESPRE SITE (foloseste-le pentru a raspunde):
${SITE_CONTEXT}

REGULI:
- Răspunde întotdeauna în română, indiferent de limba întrebării
- Fii prietenos, științific dar accesibil
- Bazează răspunsurile pe informațiile din site de mai sus
- Dacă nu găsești informația în context, spune că nu știi și sugerează să contacteze direct
- Nu inventa date medicale sau prețuri specifice
- Pentru întrebări medicale specifice, recomandă consultarea unui medic
- Promovează evaluarea C.E.L.O.S. ca punct de start pentru orice abordare personalizată

REGULI STRICTE DE LIMBĂ ROMÂNĂ:
- Folosește întotdeauna diacritice corecte: ă, â, î, ș, ț
- Respectă regulile de capitalizare românești: doar primul cuvânt al propoziției cu majusculă
- Exemplu greșit: "Nutriție Personalizată Bazată Pe Date" — Exemplu corect: "Nutriție personalizată bazată pe date"
- Numele proprii și acronimele păstrează majuscula: NutriSib, C.E.L.O.S., Radu Pascu, Sibiu, Tanita
- Ton cald, profesionist și natural în română — nu o traducere din engleză
- Evită anglicismele inutile când există echivalent românesc

FORMAT RĂSPUNS:
- Nu folosi niciodată formatare Markdown: fără asteriscuri, bold, liniuțe pentru liste, hashtag-uri
- Scrie doar în propoziții și paragrafe naturale
- Dacă enumeri ceva: "acestea includ: x, y și z"
- Răspunsuri concise, maxim 3-4 paragrafe`;

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

    return {
      statusCode: 200,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        response: data.content[0].text
      })
    };

  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Eroare server: " + error.message })
    };
  }
};
