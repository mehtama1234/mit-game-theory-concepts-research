# MIT Game Theory Concept Lab Handoff

This repository contains a transcript-backed, first-principles concept lab for MIT 14.12 Economic Applications of Game Theory, Fall 2025.

The current deliverable is a local, remotely pushed, and Sites-deployed static research site. It is not honestly a public GitHub Pages site until GitHub Pages serving is enabled and verified.

## What Is Built

- 25 clean lecture transcripts from the MIT playlist.
- 33 concept pages with plain-language first-principles explanations.
- 66 transcript-backed evidence records.
- 8 themes, 10 subthemes, 10 mathematical primitives, 9 derivation cards, and 3 method-family treatments.
- Reader surfaces for study route, recognition, math clinic, drills, solved cases, argument chains, misconception repairs, paper reading, model building, proof sketches, assumption audits, worked transfer, and capstone self-tests.
- Review surfaces:
  - `site/review-guide.html`
  - `site/publication-status.html`
  - `analysis/audits/editorial-quality-report.md`
  - `analysis/audits/publication-readiness-report.md`

## Fast Local Review

From the repository root:

```bash
python3 -m http.server 8899 --directory site
```

Open:

- `http://127.0.0.1:8899/`
- `http://127.0.0.1:8899/review-guide.html`
- `http://127.0.0.1:8899/publication-status.html`
- `http://127.0.0.1:8899/concepts/ad_auctions.html`
- `http://127.0.0.1:8899/evidence.html`

Owner-only Sites production URL:

- `https://mit-game-theory-concept-lab.manish694182.chatgpt.site`

## Validation Command

Use this before claiming a completed local pass:

```bash
python3 scripts/build_first_principles_atlas.py && \
python3 scripts/build_lecture_path.py && \
python3 scripts/build_site.py && \
python3 scripts/validate_all.py && \
python3 -m py_compile scripts/*.py && \
git diff --check
```

Expected high-level proof points:

- first-principles atlas validation passes
- site validation passes for all generated HTML files and evidence anchors
- editorial audit reports zero errors
- render audit reports zero screenshot errors
- git status is clean after committing and pushing

## Publication Boundary

`origin/main` and `origin/gh-pages` can both be pushed successfully, but that is not the same as a live public site.

The current public-hosting blocker is:

```text
Your current plan does not support GitHub Pages for this repository.
```

So the correct completion claim is:

- built locally
- validated locally
- committed and pushed to `origin/main`
- generated `site/` branch refreshed to `origin/gh-pages`
- locally reviewable through the static server
- deployed to owner-only Sites production at `https://mit-game-theory-concept-lab.manish694182.chatgpt.site`
- public GitHub Pages serving still blocked until the repository/plan/hosting state changes
- alternate Sites deployment uses `.openai/hosting.json`; do not edit or replace its `project_id`

## Main Source Artifacts

- `analysis/concepts/concept-atlas.json`
- `analysis/themes/theme-map.json`
- `analysis/themes/subtheme-map.json`
- `analysis/evidence/evidence-ledger.json`
- `analysis/lectures/lecture-path.json`
- `analysis/throughlines/primitives.json`
- `analysis/throughlines/derivations.json`
- `analysis/throughlines/method-families.json`
- `analysis/throughlines/review-guide.json`
- `analysis/throughlines/publication-status.json`
- `analysis/editorial-overrides/`
- `.openai/hosting.json`
- `package.json`
- `app/page.tsx`

## Build Scripts

- `scripts/build_first_principles_atlas.py`
- `scripts/build_lecture_path.py`
- `scripts/build_site.py`
- `scripts/validate_first_principles_atlas.py`
- `scripts/validate_site.py`
- `scripts/validate_handoff.py`
- `scripts/audit_editorial_quality.py`
- `scripts/audit_site_render.py`
- `scripts/audit_publication_readiness.py`
- `scripts/validate_all.py`
- `scripts/prepare_sites_public.mjs`
- `scripts/finalize_sites_dist.mjs`

## Sites Deployment Wrapper

The canonical research site is generated into `site/`. For Sites deployment, the npm wrapper mirrors `site/` into ignored `public/` assets, uses Vinext to build a minimal app, and copies `.openai/hosting.json` into `dist/.openai/hosting.json`.

```bash
npm run check:site-app
npm run build
```

The Sites project id is stored in `.openai/hosting.json`. Treat it as opaque and reuse it exactly.

Current Sites deployment:

- project id: `appgprj_6a6e49173ac081919d10d18ab8e47e9d`
- URL: `https://mit-game-theory-concept-lab.manish694182.chatgpt.site`
- access: owner-only custom access; unauthenticated HTTP checks return `401`
- exact latest version and deployment ids should be checked with the Sites deployment status tool after each deploy

## Push And Generated-Site Refresh

After validation and commits:

```bash
git push origin main
tmp_branch="publish-site-$(date +%s)" && \
  git subtree split --prefix site -b "$tmp_branch" && \
  git push origin "$tmp_branch:gh-pages" && \
  git branch -D "$tmp_branch"
```

Then verify:

```bash
git status --short --branch
git log -1 --oneline
git ls-remote --heads origin main gh-pages
git ls-tree -r --name-only origin/gh-pages | rg '^(index.html|review-guide.html|publication-status.html|concepts/ad_auctions.html)$'
```

## What To Improve Next

- Manual qualitative review of the weakest concept pages listed in `analysis/audits/editorial-quality-report.md`.
- More transcript-window spot checks for lecture faithfulness.
- More worked examples where a page still teaches mainly through prose.
- Public hosting only after the user explicitly chooses a hosting path or changes the GitHub Pages limitation.
