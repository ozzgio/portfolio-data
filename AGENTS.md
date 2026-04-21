# AGENTS.md - portfolio-data

Operational guide for coding agents working in this repository.

## Mission

Maintain the public published data artifacts consumed by `portfolio`.

This repo is a publishing layer, not the private authoring source. Content originates in the Obsidian vault and is exported here as JSON and images.

## Session startup

Read before editing:

1. `README.md`
2. `scripts/validate_content.py`
3. `articles.json`
4. `books.json`
5. `.github/workflows/generate-json.yml`

## Source of truth

Outside this repo:

- Private Obsidian vault
- Export/sync workflow that produces the published JSON and image assets

Inside this repo:

- `articles.json` and `books.json`
- mirrored copies in `data/`
- local published image assets in `images/`

## Non-negotiables

- Treat everything here as public.
- Keep root JSON files and `data/` mirrors in sync.
- Do not reintroduce a fake local Markdown-authoring workflow unless explicitly requested.
- Do not add private notes, drafts, or internal metadata.
- Preserve compatibility with `portfolio`, which fetches the root JSON files directly.

## Verification

Always run:

```bash
python3 scripts/validate_content.py
```

If validation fails, fix the contract mismatch before making broader changes.
