// functions/debug.js
export async function onRequest() {
  return new Response("Functions OK", { headers: { "content-type": "text/plain" } });
}
