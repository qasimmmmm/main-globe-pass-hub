# Plan — globepasshub.com Migration to Vercel

## Context
User states they own globepasshub.com (domain + content) and want the site
migrated for deployment on Vercel, keeping all content identical ("word to word
same"), including homepage, all pages, and every legal page. Deliverable:
a GitHub-ready repo + Vercel deployment instructions.

## Stage 1 — Recon (Orchestrator, shell/curl)
- Fetch homepage HTML, HTTP headers, robots.txt, sitemap.xml
- Identify tech stack (WordPress / Webflow / custom / SPA), full page inventory,
  assets (images/CSS/JS/fonts), and any forms or backend dependencies
- Output: page inventory + stack notes

## Stage 2 — Full mirror & extraction (Orchestrator, shell)
- Mirror the full site with wget (pages, images, CSS, JS, fonts)
- Organize into a clean static project structure
- Convert internal links to relative paths; keep all text, disclaimers, and
  legal pages byte-for-byte identical
- Output: /mnt/agents/output/globepasshub/ static site

## Stage 3 — Fidelity QA (verifier subagent)
- Spawn a verifier to compare key pages (homepage + legal pages) of the mirror
  against the live site: text content, structure, asset loading
- Fix any gaps found; re-verify

## Stage 4 — Vercel/GitHub packaging (Orchestrator)
- Add vercel.json (if needed), .gitignore, README with deploy steps
- git init + initial commit locally
- Provide exact GitHub repo creation + push + Vercel import commands
- Create a browser preview version via website_version_manager for user QA

## Constraints & Notes
- Content fidelity is the top priority: no rewriting, no redesign
- Flag any server-side functionality (application forms, payments) that a static
  mirror cannot carry over; propose static-compatible wiring
- I cannot create a GitHub repo on the user's account — deliver ready-to-push
  repo + exact commands instead
