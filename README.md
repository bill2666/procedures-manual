# Procedures Manual

Personal procedures manual for regulatory & financial analytics work at the Law Society of NSW.

## Architecture

```
Claude / Bill → Notion (CMS) → Make.com (sync) → GitHub → GitHub Actions → GitHub Pages
```

- **Notion** is the content management system — edit here or via Claude
- **Make.com** watches Notion for changes and commits markdown to this repo
- **GitHub Actions** runs the conversion script and builds the MkDocs Material site
- **GitHub Pages** hosts the published site

## Local development

```bash
pip install -r requirements.txt
mkdocs serve
```

Then open `http://127.0.0.1:8000` to preview.

## Files

| Path | Purpose |
|---|---|
| `mkdocs.yml` | MkDocs Material configuration |
| `docs/` | Markdown source files (auto-synced from Notion) |
| `scripts/convert_notion.py` | Notion callout → MkDocs admonition converter |
| `.github/workflows/build.yml` | GitHub Actions build & deploy workflow |
