// Save as: functions/auth.js  (opens GitHub's login page)
export async function onRequest({ request, env }) {
  const url = new URL(request.url);
  const state = crypto.randomUUID();
  const github = new URL('https://github.com/login/oauth/authorize');
  github.searchParams.set('client_id', env.GITHUB_CLIENT_ID);
  github.searchParams.set('redirect_uri', url.origin + '/callback');
  github.searchParams.set('scope', 'repo,user');
  github.searchParams.set('state', state);
  return new Response(null, {
    status: 302,
    headers: {
      Location: github.toString(),
      'Set-Cookie': 'oauth_state=' + state + '; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=600',
      'Cache-Control': 'no-store',
    },
  });
}
