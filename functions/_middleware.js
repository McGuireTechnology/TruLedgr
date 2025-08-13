// Cloudflare Pages Function to ensure proper MIME types
export async function onRequest(context) {
  const { request, next } = context;
  
  // Let Cloudflare handle the request normally
  const response = await next();
  
  // If it's an HTML request, make sure the content-type is correct
  if (request.url.endsWith('/') || request.url.endsWith('.html')) {
    const newResponse = new Response(response.body, response);
    newResponse.headers.set('Content-Type', 'text/html; charset=utf-8');
    return newResponse;
  }
  
  return response;
}
