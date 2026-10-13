// Proxy pour les audios externes
export const config = { runtime: 'edge' };

const ALLOWED_HOSTS = [
  'server1.mp3quran.net', 'server2.mp3quran.net', 'server3.mp3quran.net',
  'server4.mp3quran.net', 'server5.mp3quran.net', 'server6.mp3quran.net',
  'server7.mp3quran.net', 'server8.mp3quran.net', 'server9.mp3quran.net',
  'server10.mp3quran.net', 'server11.mp3quran.net', 'server12.mp3quran.net',
  'server13.mp3quran.net', 'server14.mp3quran.net', 'server15.mp3quran.net',
  'server16.mp3quran.net',
  'everyayah.com',
  'cdn.islamic.network'
];

export default async function handler(req) {
  const url = new URL(req.url);
  const targetUrl = url.searchParams.get('url');

  if (!targetUrl) return new Response('Missing url parameter', { status: 400 });

  let parsed;
  try { parsed = new URL(targetUrl); }
  catch (e) { return new Response('Invalid URL', { status: 400 }); }

  if (!ALLOWED_HOSTS.includes(parsed.hostname)) {
    return new Response('Host not allowed', { status: 403 });
  }

  try {
    const upstream = await fetch(targetUrl, {
      headers: { 'Range': req.headers.get('range') || '' }
    });

    const headers = new Headers();
    headers.set('Content-Type', upstream.headers.get('content-type') || 'audio/mpeg');
    headers.set('Cache-Control', 'public, max-age=86400');
    headers.set('Access-Control-Allow-Origin', '*');
    headers.set('Accept-Ranges', 'bytes');

    const contentLength = upstream.headers.get('content-length');
    if (contentLength) headers.set('Content-Length', contentLength);

    const contentRange = upstream.headers.get('content-range');
    if (contentRange) headers.set('Content-Range', contentRange);

    return new Response(upstream.body, { status: upstream.status, headers });
  } catch (e) {
    return new Response('Proxy error: ' + e.message, { status: 502 });
  }
}
