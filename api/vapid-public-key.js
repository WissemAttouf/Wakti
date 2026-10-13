export const config = { runtime: 'edge' };

export default async function handler() {
  const publicKey = process.env.VAPID_PUBLIC_KEY;

  if (!publicKey) {
    return new Response(JSON.stringify({ error: 'VAPID_PUBLIC_KEY not configured' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-store'
      }
    });
  }

  return new Response(JSON.stringify({ key: publicKey }), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=86400'
    }
  });
}