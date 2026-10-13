export const config = {
  runtime: 'nodejs',
  maxDuration: 5
};

export default async function handler(req, res) {
  // Support des 2 formats : nouvelle cle (sb_publishable_...) et ancien JWT (eyJ...)
  const url = process.env.SUPABASE_URL || '';
  const key = process.env.SUPABASE_PUBLISHABLE_KEY
           || process.env.SUPABASE_ANON_KEY
           || '';

  if (!url || !key) {
    return res.status(200).json({
      configured: false,
      hint: 'Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in Vercel'
    });
  }

  res.setHeader('Cache-Control', 'public, max-age=3600');
  return res.status(200).json({
    configured: true,
    url: url,
    anonKey: key
  });
}
