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

function doPost(e) {
  let d = {};
  try { d = JSON.parse(e.postData.contents); } catch (err) { return out_({ ok: false, error: 'Invalid request' }); }
  if (!SECRET || SECRET === 'PASTE-SECRET-HERE' || d.secret !== SECRET) return out_({ ok: false, error: 'Forbidden' });
  send_(d);
  return out_({ ok: true });
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
