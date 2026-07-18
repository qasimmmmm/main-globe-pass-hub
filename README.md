# GlobePassHub — Static Build (Vercel-ready)

A static, prerendered copy of **globepasshub.com** (all public pages), packaged for
deployment on Vercel. All page content, text, design, and legal pages are preserved
as-is from the original site.

## What's included

- `index.html` + one folder per route (e.g. `faqs/index.html`, `privacy-policy/index.html`)
  — 35 pages total: homepage, FAQs, About, Contact, Disclaimer, all legal pages
  (Privacy Policy, Terms & Conditions, Refund Policy, Cookie Policy, Legal Notice),
  Canada eTA pages (EN/ES + requirement pages), Study Permit, Visitor Visa,
  US ESTA pages (EN/ES), application form pages, thank-you pages, and the login page.
- `build/assets/` — original compiled JS/CSS bundles
- `fonts/`, `img/`, `favicon.ico` — original assets
- `vercel.json` — clean URLs + immutable caching for static assets

## Deploy to Vercel via GitHub (recommended)

```bash
# 1. Create a new EMPTY repo on github.com (e.g. "globepasshub"), then:
git remote add origin https://github.com/<your-username>/globepasshub.git
git branch -M main
git push -u origin main
```

2. Go to [vercel.com](https://vercel.com) → **Add New… → Project** → **Import** the repo.
3. Vercel detects it as a static site ("Other" framework preset). No build command,
   no output directory setting needed — just click **Deploy**.
4. In **Settings → Domains**, add `globepasshub.com` (and `www`) and update your DNS
   records as Vercel instructs.

## Alternative: Vercel CLI (no GitHub needed)

```bash
npm i -g vercel
cd <this folder>
vercel --prod
```

## Important limitations (please read)

This is a **static** copy. The original site runs on a Laravel backend, so the
following features **render visually but cannot process data** on Vercel:

- Application forms (Canada eTA / ESTA / Study Permit / Visitor Visa submission)
- Login / admin panel (`/login-gest`, `/dashboard`, …)
- Payments / checkout
- Contact form delivery
- Language cookie/session switching

When a visitor submits a form, a small "Backend not connected" notice is shown
instead of a broken page. To remove that notice later, delete the `<script>` block
containing `__staticNotice` from the `<head>` of each HTML file.

To make forms work again, you would need to either:
- keep the Laravel backend running somewhere (VPS, Laravel Forge, Railway, …) and
  point the forms' API endpoints to it, or
- rebuild the forms with a serverless backend (Vercel Functions, etc.).

## Notes on source-site quirks (preserved faithfully)

- `/eta-canada-exigences` (FR) and `/eta-kanada-voraussetzungen` (DE) render empty
  on the original site as well (the `Public/Requisitos` component outputs nothing).
- `/politica-de-reembolso/` returns 404 on the original site (one outdated link in
  the refund text points there; the working page is `/refund-policy`).
