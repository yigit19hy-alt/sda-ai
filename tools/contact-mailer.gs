/**
 * SDA AI Services – contact form mailer (Google Apps Script)
 *
 * Receives requests from the website's contact form (functions/api/contact.js)
 * and sends them from the Google Workspace mailbox to TO.
 *
 * Setup (signed in as yigit@sda-services.ai):
 *   1. script.google.com > New project > replace the code with this file.
 *   2. Set SECRET below to a long random value (the same value goes into
 *      Cloudflare as MAIL_SECRET).
 *   3. Run "test" once: allow the permission, a test mail arrives in TO.
 *   4. Deploy > New deployment > type "Web app":
 *        Execute as: Me   ·   Who has access: Anyone
 *      Copy the web app URL (ends in /exec).
 *   5. Cloudflare > Workers & Pages > sda-ai > Settings > Variables and secrets:
 *        MAIL_WEBHOOK = web app URL,  MAIL_SECRET = SECRET (type: Secret)
 *      Then redeploy the site (or push a commit).
 *
 * After changing this code: Deploy > Manage deployments > edit > Version "New version".
 */
const TO = 'yigit@sda-services.ai';
const SECRET = 'PASTE-SECRET-HERE';
const BOOKING_URL = 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ0NwR_cV6fana6F9QDSuWfoKAGoRw3_kfl0jSYuho7E-LeVSI1pGvLhfV6qC5lEAHz7iyCo_OBK';
const WHATSAPP = '+971 54 237 7342';
const WHATSAPP_URL = 'https://wa.me/971542377342';
const CONFIRM_CAP = 40;  // max. confirmation mails per 6 hours (protects against abuse of the form)

function doPost(e) {
  let d = {};
  try { d = JSON.parse(e.postData.contents); } catch (err) { return out_({ ok: false, error: 'Invalid request' }); }
  if (!SECRET || SECRET === 'PASTE-SECRET-HERE' || d.secret !== SECRET) return out_({ ok: false, error: 'Forbidden' });
  send_(d);
  try { confirm_(d); } catch (err) { console.warn('Confirmation not sent: ' + err); }
  return out_({ ok: true });
}

/**
 * Short automatic confirmation to the person who sent the form.
 * Never repeats what they typed (only a plain first name), so it cannot be used to send spam,
 * and is limited to one mail per address every 6 hours and CONFIRM_CAP mails per 6 hours.
 */
function confirm_(d) {
  const email = String(d.email || '').trim().slice(0, 200);
  if (!/^[^\s@<>()",;:]+@[^\s@<>()",;:]+\.[^\s@<>()",;:]{2,}$/.test(email)) return;
  const cache = CacheService.getScriptCache();
  const key = 'confirm:' + email.toLowerCase();
  if (cache.get(key)) return;
  const count = Number(cache.get('confirm-count') || 0);
  if (count >= CONFIRM_CAP) return;
  cache.put(key, '1', 21600);
  cache.put('confirm-count', String(count + 1), 21600);

  const first = String(d.name || '').trim().split(/\s+/)[0];
  const hello = /^[\p{L}][\p{L}'-]{0,29}$/u.test(first) ? 'Hi ' + first + ',' : 'Hello,';
  const body = [
    hello,
    '',
    'thank you for contacting SDA AI Services. We have received your request and will reply within one business day with first ideas and a proposed next step.',
    '',
    'Want to talk sooner? Book a free 30-minute call at a time that suits you:',
    BOOKING_URL,
    '',
    'Or message us on WhatsApp: ' + WHATSAPP,
    WHATSAPP_URL,
    '',
    'Best regards',
    'SDA AI Services',
    'Software, Development, Applications & AI Services',
    'Meydan Grandstand, Dubai, United Arab Emirates',
    'https://sda-services.ai',
    '',
    'This is an automatic confirmation. Simply reply to this email if you want to add anything.',
  ].join('\n');
  MailApp.sendEmail(email, 'We received your request – SDA AI Services', body, { name: 'SDA AI Services', replyTo: TO });
}

function send_(d) {
  const s = (v, n) => String(v || '').replace(/[\r\n]+/g, ' ').trim().slice(0, n);
  const email = s(d.email, 200), name = s(d.name, 120);
  const subject = 'New request: ' + (s(d.topic, 80) || 'Website') + ' – ' + name;
  const body = [
    'Name: ' + name,
    'Email: ' + email,
    'Company: ' + s(d.company, 160),
    'Topic: ' + s(d.topic, 80),
    'Received: ' + s(d.at, 40),
    '',
    String(d.message || '').slice(0, 5000),
  ].join('\n');
  const opts = { name: 'SDA AI Services Website' };
  if (/^[^\s@<>()",;:]+@[^\s@<>()",;:]+\.[^\s@<>()",;:]{2,}$/.test(email)) opts.replyTo = email;
  MailApp.sendEmail(TO, subject, body, opts);
}

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

/** Run once in the editor to grant the permission and check delivery. */
function test() {
  send_({ name: 'Test', email: TO, company: 'SDA AI Services', topic: 'Setup test', at: new Date().toISOString(), message: 'The contact form mailer works.' });
}
