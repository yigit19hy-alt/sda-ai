# SDA AI Services – website

Static website for SDA AI Services: AI agents, workflow automation, custom web and mobile apps, data management and enterprise integration. It includes six interactive demos that run in the browser.

## Structure

| Path | What it is |
|---|---|
| `build.py` | All page content and templates. Run it to regenerate `site/`. |
| `src/assets/` | Styles (`style.css`), site scripts (`main.js`), demo apps (`demos.js`), logo set (`brand/`), security headers (`../_headers`) |
| `site/` | **The finished website** (16 content pages + legal pages, sitemap, robots, manifest). This is what Cloudflare serves. |
| `functions/api/contact.js` | Cloudflare Pages Function that receives the contact form |
| `tools/` | Logo generator (`make_logo.py`, `render_png.js`) and the Geist font (SIL Open Font License) |

## Edit and rebuild

```bash
python3 build.py
```

Logo (only needed if you change it):

```bash
pip install fonttools brotli && python3 tools/make_logo.py && node tools/render_png.js
```

## Deploy on Cloudflare Pages

1. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** → **Connect to Git** → choose `HYigit19/sda-ai`.
2. Build settings: **Framework preset** None, **Build command** `python3 build.py` (or leave empty, `site/` is committed), **Build output directory** `site`.
3. **Save and Deploy**. The site goes live at `https://<project>.pages.dev`. Every push to `main` deploys again.

### Contact form

The form posts to `/api/contact` (`functions/api/contact.js`). Every request goes to **yigit@sda-services.ai** (`TO` in `contact.js`).

Delivery through the Google Workspace mailbox (free):

1. Set up `tools/contact-mailer.gs` as a Google Apps Script web app (steps at the top of that file).
2. In the Pages project open **Settings → Variables and secrets** and add `MAIL_WEBHOOK` (web app URL) and `MAIL_SECRET` (secret, same value as `SECRET` in the script). Redeploy.

Optional: `RESEND_API_KEY` (+ `CONTACT_FROM`) as a fallback sender, and a **KV namespace** binding `CONTACTS` to keep a copy of every request.

Without any of these, the form tells visitors to email yigit@sda-services.ai directly.

## Before launch

- [x] `EMAIL` in `build.py` is set to `yigit@sda-services.ai`.
- [x] `SITE_URL` in `build.py` is set to `https://sda-services.ai`.
- [x] Privacy policy and legal notice filled in (`privacy()` and `legal()` in `build.py`). Have them reviewed.
- [ ] Optional values at the top of `build.py`: `PHONE`, `WHATSAPP`, `SOCIAL`, `LICENSE_NO`. Empty values are left out of the pages automatically.
- [ ] After switching on Cloudflare Web Analytics, set `ANALYTICS = True` so the privacy policy mentions it.
- [ ] Configure the contact form mailer (see above).
- Rebuild with `python3 build.py`, commit and push.

## Content

| Where | What |
|---|---|
| `build.py` | Services, pricing, homepage, about, contact, legal pages |
| `src/landing.py` | SEO landing pages: industries, regions (incl. Dubai), solutions. Keep each page unique. |
| `src/insights.py` | Insights articles (blog). New article = new entry in `POSTS`. |
| `src/lastmod.json` | Written by the build: the sitemap date of a page changes only when its content changes. |
| `src/assets/fonts/` | Self-hosted Geist fonts (SIL Open Font License), no Google Fonts requests. |
