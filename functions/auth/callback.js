export async function onRequest(context) {
  const url = new URL(context.request.url);

  const code = url.searchParams.get("code");

  if (!code) {
    return new Response("Missing code", { status: 400 });
  }

  const response = await fetch(
    "https://github.com/login/oauth/access_token",
    {
      method: "POST",
      headers: {
        Accept: "application/json",
      },
      body: new URLSearchParams({
        client_id: context.env.GITHUB_CLIENT_ID,
        client_secret: context.env.GITHUB_CLIENT_SECRET,
        code,
      }),
    }
  );

  const data = await response.json();

  return new Response(
    `
    <!doctype html>
    <html>
      <head>
        <title>Authorizing...</title>
      </head>
      <body>
        <script>
          (function() {
            const message = {
              token: "${data.access_token}",
              provider: "github"
            };

            window.opener.postMessage(
              "authorization:" + JSON.stringify(message),
              window.location.origin
            );

            window.close();
          })();
        </script>
      </body>
    </html>
    `,
    {
      headers: {
        "content-type": "text/html",
      },
    }
  );
}
