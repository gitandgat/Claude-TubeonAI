import { kv } from '@vercel/kv';

export const config = {
  matcher: '/',
};

export default async function middleware(req) {
  const cookieHeader = req.headers.get('cookie') || '';
  const cookies = Object.fromEntries(
    cookieHeader.split(';').map(c => c.trim().split('=')).filter(p => p.length === 2)
  );

  const code = cookies.access ? decodeURIComponent(cookies.access) : null;
  const subscriberId = code ? await kv.get(`code:${code}`) : null;

  if (!subscriberId) {
    return Response.redirect(new URL('/login.html', req.url));
  }
}
