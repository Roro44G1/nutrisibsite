exports.handler = async function(event) {
  var CORS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers: CORS, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers: CORS, body: 'Method Not Allowed' };
  }

  var apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return {
      statusCode: 500,
      headers: CORS,
      body: JSON.stringify({ error: { message: 'API key lipsa' } })
    };
  }

  var parsedBody;
  try {
    parsedBody = JSON.parse(event.body);
  } catch(e1) {
    return {
      statusCode: 400,
      headers: CORS,
      body: JSON.stringify({ error: { message: 'JSON invalid' } })
    };
  }

  var responseText;
  var responseStatus;
  try {
    var response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(parsedBody)
    });
    responseStatus = response.status;
    responseText = await response.text();
  } catch(e2) {
    return {
      statusCode: 500,
      headers: CORS,
      body: JSON.stringify({ error: { message: e2.message } })
    };
  }

  return {
    statusCode: responseStatus,
    headers: CORS,
    body: responseText
  };
};