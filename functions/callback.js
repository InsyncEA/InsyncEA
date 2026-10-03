// Save as: functions/callback.js  (GitHub sends people back here after login)
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');
  const saved = (request.headers.get('Cookie') || '').match(/(?:^|;\s*)oauth_state=([^;]+)/);

  if (!code) return page('error', 'GitHub did not send a login code.');
  if (!saved || saved[1] !== state) return page('error', 'The login check failed. Close this window and try again.');

  let data;
  try {
    const res = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json', 'User-Agent': 'insyncea-decap-oauth' },
      body: JSON.stringify({ client_id: env.GITHUB_CLIENT_ID, client_secret: env.GITHUB_CLIENT_SECRET, code }),
    });
    data = await res.json();
  } catch (e) {
    return page('error', 'Could not reach GitHub: ' + e.message);
  }
  if (!data.access_token) {
    return page('error', 'GitHub said: ' + (data.error_description || data.error || 'no token was returned'));
  }
  return page('success', { token: data.access_token, provider: 'github' });
}

function page(status, content) {
  const message =
    status === 'success'
      ? 'authorization:github:success:' + JSON.stringify(content)
      : 'authorization:github:error:' + JSON.stringify({ message: content });
  const safe = JSON.stringify(message).replace(/</g, '\\u003c');
  const text = status === 'success' ? 'Login successful. This window will close.' : content;
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>Authorizing</title></head>
<body style="font-family:sans-serif;padding:24px"><p id="t"></p>
<script>
(function () {
  var msg = ${safe};
  document.getElementById('t').textContent = ${JSON.stringify(text).replace(/</g, '\\u003c')};
  function receive(e) { window.opener.postMessage(msg, e.origin); }
  window.addEventListener('message', receive, false);
  if (window.opener) { window.opener.postMessage('authorizing:github', '*'); }
  else { document.getElementById('t').textContent += ' (This window lost its connection to the CMS. Close it and click Login again.)'; }
})();
</script></body></html>`;
  return new Response(html, {
    headers: {
      'Content-Type': 'text/html;charset=UTF-8',
      'Cache-Control': 'no-store',
      'Set-Cookie': 'oauth_state=; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=0',
    },
  });
}
