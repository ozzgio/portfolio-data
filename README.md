# Portfolio Data

Public repository containing the published data artifacts for the portfolio site.

For agent-facing repo rules, see [AGENTS.md](./AGENTS.md).

## Workflow

Current source of truth:

`Obsidian vault -> exported JSON/images -> portfolio-data -> portfolio`

This repo is no longer the authoring location for Markdown content. It is the public publishing layer consumed by the website.

## What lives here

- `articles.json` and `books.json`: public metadata payloads
- `data/articles.json` and `data/books.json`: mirrored copies used by the site/runtime
- `images/`: article thumbnails and other published image assets
- `scripts/validate_content.py`: fails fast when published artifacts are malformed

## What does not live here

- private vault notes
- draft-only content not meant for publication
- the canonical Obsidian authoring workflow
- frontend rendering code from `portfolio`

## Validation

GitHub Actions validates changes on push and pull request. The validator checks:

- required fields and JSON structure
- `articles.json` and `data/articles.json` stay in sync
- `books.json` and `data/books.json` stay in sync
- article thumbnails exist in `images/`
- URLs are absolute `http`/`https`
- dates use `YYYY-MM-DD`
- ratings stay in the `0..5` range

Run it locally:

```bash
python3 scripts/validate_content.py
```

## Publishing rules

When updating this repo from Obsidian or another export step:

1. Update both root JSON files and their `data/` mirrors together.
2. Add any new local article thumbnails under `images/`.
3. Run `python3 scripts/validate_content.py` before pushing.
4. Treat this repo as public. Do not publish private notes or internal-only metadata here.

## Repository structure

```text
portfolio-data/
├── articles.json
├── books.json
├── data/
│   ├── articles.json
│   └── books.json
├── images/
├── scripts/
│   ├── generate_json.py
│   └── validate_content.py
└── .github/workflows/
```
