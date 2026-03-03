# Portfolio Data

Public repository containing the content and data for my portfolio/blog.

## 🚀 Workflow

This repository hosts the source Markdown files for Articles and Books. A GitHub Action automatically generates the JSON files used by the website whenever changes are pushed.

### Adding a New Book

1. Create a new Markdown file in `blog/books/` (e.g., `blog/books/my-new-book.md`).
2. Use the following frontmatter format:

```markdown
---
title: "Book Title"
author: "Author Name"
cover: "https://example.com/cover.jpg"
rating: 4.5
tags:
  - Philosophy
  - Finance
status: "read"
---

Your lesson or notes here...
```

3. Commit and push the changes.
4. The `books.json` file will be automatically updated.

### Adding a New Article

1. Create a new Markdown file in `blog/articles/YYYY/published/` (e.g., `blog/articles/2025/published/my-article.md`).
2. Place any images in `blog/articles/images/`.
3. Use the following frontmatter format:

```markdown
---
title: "Article Title"
date: "2025-01-01"
description: "Brief description"
url: "https://external-link.com"
thumbnail: "image.png"
tags:
  - Tech
status: "published"
---

Content...
```

4. Commit and push.

## 📁 Repository Structure

```
portfolio-data/
├── blog/                # Source Markdown files
│   ├── articles/        # Articles organized by year
│   └── books/           # Book notes
├── articles.json        # Generated metadata for articles
├── books.json           # Generated metadata for books
├── images/              # Images used in articles/books
├── scripts/             # Generation scripts
└── .github/workflows/   # Automation configuration
```
