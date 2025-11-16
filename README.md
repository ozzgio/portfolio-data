# Portfolio Data

Public repository containing JSON data and images for my portfolio/blog. This repository includes Python scripts for migrating content from Notion to Obsidian vault and generating JSON files for use in web applications.

## 📁 Repository Structure

```
portfolio-data/
├── data/
│   ├── articles.json    # Published articles metadata
│   ├── books.json       # Books I've read
│   └── images/          # Article thumbnails
├── scripts/
│   └── generate_json.py # Script to generate JSON from Obsidian Markdown
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ozzgio/portfolio-data.git
   cd portfolio-data
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install pyyaml
   ```

### Using the Scripts

#### Generating JSON from Obsidian Vault

The `generate_json.py` script converts Obsidian Markdown files with YAML frontmatter into JSON files for use in web applications.

**Expected Obsidian Vault Structure:**
```
your-obsidian-vault/
├── blog/
│   ├── articles/
│   │   ├── YYYY/
│   │   │   └── published/
│   │   │       └── article-name.md
│   │   └── images/
│   │       └── *.png, *.jpg, etc.
│   └── books/
│       └── book-name.md
```

**Article Markdown Format:**
```markdown
---
title: "Article Title"
date: "2024-01-15"
description: "Article description"
url: "https://example.com/article"
thumbnail: "image-name.png"
status: "published"
tags:
  - Tech
  - Rails
---

Article content here...
```

**Book Markdown Format:**
```markdown
---
title: "Book Title"
author: "Author Name"
cover: "cover-url.jpg"
rating: 4.5
status: "read"
url: "https://example.com/book"
tags:
  - Programming
  - Design
---

Book notes here...
```

**Run the script:**

The script can be run in several ways:

```bash
# Option 1: From your Obsidian vault root directory (default behavior)
cd /path/to/your-obsidian-vault
python3 /path/to/portfolio-data/scripts/generate_json.py

# Option 2: Specify vault path and output directory
python3 /path/to/portfolio-data/scripts/generate_json.py /path/to/your-obsidian-vault /path/to/output

# Option 3: From portfolio-data directory, pointing to your vault
cd /path/to/portfolio-data
python3 scripts/generate_json.py /path/to/your-obsidian-vault

# Option 4: Dry run to preview changes without modifying files
python3 scripts/generate_json.py --dry-run /path/to/your-obsidian-vault

# Get help
python3 scripts/generate_json.py --help
```

**Command-line arguments:**
- `vault_path` (optional): Path to Obsidian vault root. Defaults to current directory.
- `output_path` (optional): Path to output directory. Defaults to `./data`.
- `--dry-run`: Preview what would be done without making any changes.
- `--help` or `-h`: Show help message with usage examples.

The script will:
- Extract metadata from all published articles in `blog/articles/YYYY/published/`
- Extract metadata from all read books in `blog/books/`
- Copy images from `blog/articles/images/` to `data/images/`
- Generate `data/articles.json` and `data/books.json`

## 📊 Data Files

### `data/articles.json`
Contains metadata for published articles:
- `title`: Article title
- `date`: Publication date (YYYY-MM-DD)
- `description`: Article description/excerpt
- `url`: Link to the full article
- `thumbnail`: Image filename (stored in `data/images/`)
- `tags`: Array of tag strings

### `data/books.json`
Contains books I've read:
- `title`: Book title
- `author`: Author name
- `cover`: Cover image URL
- `rating`: Rating (0-5, float)
- `url`: Link to book (optional)
- `tags`: Array of tag strings

## 🔄 Migration Workflow (Notion → Obsidian → JSON)

This repository is part of a migration workflow from Notion to Obsidian:

1. **Export from Notion:** Export your Notion pages as Markdown
2. **Import to Obsidian:** Import the Markdown files into your Obsidian vault
3. **Organize:** Structure files according to the expected format above
4. **Generate JSON:** Run `generate_json.py` to create JSON files
5. **Deploy:** Use the JSON files in your portfolio/blog application

The script works with standard Markdown files that have YAML frontmatter, so it's compatible with content exported from Notion, Obsidian, or any other Markdown-based system.

## 🌐 Using the Data

### Fetching from GitHub

You can fetch the JSON files directly from GitHub:

```javascript
// Fetch articles
const articles = await fetch('https://raw.githubusercontent.com/ozzgio/portfolio-data/main/data/articles.json')
  .then(res => res.json());

// Fetch books
const books = await fetch('https://raw.githubusercontent.com/ozzgio/portfolio-data/main/data/books.json')
  .then(res => res.json());
```

### Local Development

For local development, you can:
1. Clone this repository
2. Run the script to generate fresh JSON files
3. Use the JSON files in your local development environment

## 🔧 Script Details

The `generate_json.py` script:
- ✅ Works with or without `pyyaml` (has a fallback parser)
- ✅ Handles YAML frontmatter parsing
- ✅ Filters articles by `status: published` or presence of `url`
- ✅ Filters books by `status: read` or presence of `rating`
- ✅ Sorts articles by date (newest first)
- ✅ Sorts books by rating (highest first)
- ✅ Copies images to the data directory
- ✅ Handles errors gracefully
- ✅ **Security features:**
  - Path validation to prevent path traversal attacks
  - File size limits (50 MB for images, 10 MB for markdown files)
  - Filename sanitization to prevent malicious file names
  - Safe path resolution and validation
- ✅ **User-friendly features:**
  - `--help` flag for usage information
  - `--dry-run` mode to preview changes
  - Clear error messages and warnings
  - Overwrite warnings for existing files
  - Progress feedback during execution

## 🔄 Auto-Update

This repository is automatically updated via GitHub Actions when new articles or books are published in the private Obsidian vault.

## 📝 License

This data is public and can be used for reference or educational purposes.

