// netlify/functions/claude-proxy.js

exports.handler = async function(event) {

  const headers = {
    'Access-Control-Allow-Origin':  '*',
    'Access-Control-Allow-Headers': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 200, headers, body: JSON.stringify({ error: 'Trimite POST' }) };
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return { statusCode: 200, headers, body: JSON.stringify({ error: 'API key lipsa' }) };
  }

  try {
    const payload = JSON.parse(event.body || '{}');

    const resp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type':      'application/json',
        'x-api-key':         apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(payload),
    });

    const rawText = await resp.text();
    console.log('STATUS:', resp.status);
    console.log('BODY:', rawText.substring(0, 500));

    let data;
    try { data = JSON.parse(rawText); }
    catch(e) { return { statusCode: 200, headers, body: JSON.stringify({ error: 'JSON invalid', raw: rawText.substring(0,300) }) }; }

    // Returnează tot răspunsul brut — inclusiv erori Anthropic
    return { statusCode: 200, headers, body: JSON.stringify(data) };

  } catch (err) {
    return { statusCode: 200, headers, body: JSON.stringify({ error: 'Proxy: ' + err.message }) };
  }
};
