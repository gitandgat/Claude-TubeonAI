import { kv } from '@vercel/kv';
import nodemailer from 'nodemailer';

function generateAccessCode() {
  return Array.from({ length: 3 }, () =>
    Math.random().toString(36).slice(2, 6)
  ).join('-');
}

async function sendAccessCodeEmail(email, accessCode) {
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST,
    port: Number(process.env.SMTP_PORT),
    secure: false,
    auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASSWORD },
  });

  await transporter.sendMail({
    from: process.env.SMTP_FROM,
    to: email,
    subject: 'Your Viral Hooks access code',
    text: `Welcome to Viral Hooks!\n\nYour access code: ${accessCode}\n\nGo to https://viral-hooks-deploy.vercel.app and enter this code to log in.\n\n- Crosswalk Wisdom`,
  });
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const params = req.body;
  const productPermalink = params.product_permalink || params['product_permalink'];

  if (productPermalink !== process.env.GUMROAD_PRODUCT_PERMALINK) {
    return res.status(200).json({ ok: true, ignored: true });
  }

  const email = params.email;
  const subscriberId = params.subscription_id || params.sale_id;

  if (!email || !subscriberId) {
    return res.status(400).json({ error: 'Missing email or subscriber id' });
  }

  const isCancellation =
    params.cancelled === 'true' ||
    params.refunded === 'true' ||
    params.subscription_ended_at ||
    params.subscription_cancelled_at;

  if (isCancellation) {
    const existingCode = await kv.get(`subscriber:${subscriberId}`);
    if (existingCode) {
      await kv.del(`code:${existingCode}`);
      await kv.del(`subscriber:${subscriberId}`);
    }
    return res.json({ ok: true, revoked: true });
  }

  // New sale / subscription charge
  const existingCode = await kv.get(`subscriber:${subscriberId}`);
  if (existingCode) {
    return res.json({ ok: true, alreadyExists: true });
  }

  const accessCode = generateAccessCode();
  await kv.set(`code:${accessCode}`, subscriberId);
  await kv.set(`subscriber:${subscriberId}`, accessCode);

  await sendAccessCodeEmail(email, accessCode);

  res.json({ ok: true, created: true });
}
