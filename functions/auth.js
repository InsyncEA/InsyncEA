export async function onRequest(context) {
  const url = new URL(context.request.url);

  const clientId = context.env.GITHUB_CLIENT_ID;
  const redirectUri = `${url.origin}/auth/callback`;

  const githubUrl =
    "https://github.com/login/oauth/authorize" +
    `?client_id=${clientId}` +
    `&scope=repo` +
    `&redirect_uri=${redirectUri}`;

  return Response.redirect(githubUrl, 302);
}
