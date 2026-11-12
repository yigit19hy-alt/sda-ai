// Cloudflare Pages Function: POST /api/contact
// Every request is sent to TO (below). Delivery, in this order:
//   1. Google Workspace via Apps Script web app (tools/contact-mailer.gs):
//      Pages project > Settings > Variables and secrets: MAIL_WEBHOOK (web app URL), MAIL_SECRET (secret)
//   2. Resend (optional fallback): RESEND_API_KEY (secret), CONTACT_FROM (verified sender, optional)
// Optional: KV binding "CONTACTS" keeps a copy of every request.
const TO = 'yigit@sda-services.ai';

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const clean = (v, max) => String(v || '').trim().slice(0, max);

async function viaAppsScript(env, entry) {
  if (!env.MAIL_WEBHOOK) return false;
  try {
    const r = await fetch(env.MAIL_WEBHOOK, {
      method: 'POST', redirect: 'follow',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ secret: env.MAIL_SECRET || '', ...entry }),
    });
    const j = await r.json().catch(() => ({}));
    return r.ok && j.ok === true;
  } catch { return false; }
}

async function viaResend(env, entry) {
  if (!env.RESEND_API_KEY) return false;
  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: env.CONTACT_FROM || 'SDA Website <onboarding@resend.dev>', to: [TO], reply_to: entry.email,
        subject: `New request: ${entry.topic || 'Website'} – ${entry.name}`,
        text: `Name: ${entry.name}\nEmail: ${entry.email}\nCompany: ${entry.company}\nTopic: ${entry.topic}\n\n${entry.message}`,
      }),
    });
    return r.ok;
  } catch { return false; }
}

export async function onRequestPost({ request, env }) {
  let d = {};
  const type = request.headers.get('Content-Type') || '';
  try {
    d = type.includes('application/json') ? await request.json() : Object.fromEntries(await request.formData());
  } catch { return json({ ok: false, error: 'Invalid request' }, 400); }

  if (d['company-website']) return json({ ok: true });            // honeypot: silently accept bots
  const entry = {
    name: clean(d.name, 120), email: clean(d.email, 200), company: clean(d.company, 160),
    topic: clean(d.topic, 80), message: clean(d.message, 5000),
    at: new Date().toISOString(), ip: request.headers.get('CF-Connecting-IP') || '',
  };
  if (!entry.name) return json({ ok: false, error: 'Please add your name.' }, 400);
  if (!/^\S+@\S+\.\S+$/.test(entry.email)) return json({ ok: false, error: 'Please enter a valid email.' }, 400);

  let stored = false;
  if (env.CONTACTS) { await env.CONTACTS.put(`contact:${entry.at}:${crypto.randomUUID()}`, JSON.stringify(entry)); stored = true; }
  const mailed = (await viaAppsScript(env, entry)) || (await viaResend(env, entry));

  if (!stored && !mailed) return json({ ok: false, error: 'The contact form is not configured yet.' }, 503);
  return json({ ok: true });
}

export const onRequest = () => json({ ok: false, error: 'Use POST' }, 405);
