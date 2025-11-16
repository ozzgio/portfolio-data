# Portfolio Data

Public repository containing JSON data and images for my portfolio/blog.

## 📁 Structure

```
portfolio-data/
├── data/
│   ├── articles.json    # Published articles metadata
│   ├── books.json       # Books I've read
│   └── images/          # Article thumbnails
├── scripts/
│   └── generate_json.py # Script to generate JSON from Markdown
└── README.md
```

## 📊 Data Files

### `data/articles.json`
Contains metadata for published articles:
- Title, date, description
- URL to the article
- Thumbnail image
- Tags

### `data/books.json`
Contains books I've read:
- Title, author
- Rating (0-5)
- Cover image URL
- Tags

## 🚀 Usage

### Fetching the Data

You can fetch the JSON files directly from GitHub:

```javascript
// Fetch articles
const articles = await fetch('https://raw.githubusercontent.com/ozzgio/portfolio-data/main/data/articles.json')
  .then(res => res.json());

// Fetch books
const books = await fetch('https://raw.githubusercontent.com/ozzgio/portfolio-data/main/data/books.json')
  .then(res => res.json());
```

### Generating JSON (Local Development)

If you want to generate the JSON files locally:

```bash
# Install dependencies
pip install pyyaml

# Run the script (from the Obsidian vault root)
python3 scripts/generate_json.py
```

**Note:** The script expects to be run from the Obsidian vault root directory where `blog/articles/` and `blog/books/` folders exist.

## 🔄 Auto-Update

This repository is automatically updated via GitHub Actions when new articles or books are published in the private Obsidian vault.

## 📝 License

This data is public and can be used for reference or educational purposes.

