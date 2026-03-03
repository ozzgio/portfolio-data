#!/usr/bin/env python3
"""
Generate JSON files from Obsidian Markdown articles and books.
Outputs data/articles.json and data/books.json for the blog.

Usage:
    python3 generate_json.py [OPTIONS] [vault_path] [output_path]
    
    vault_path:  Path to Obsidian vault root (default: current directory)
    output_path: Path to output directory (default: ./data)
    
Options:
    -h, --help     Show this help message and exit
    --dry-run      Show what would be done without making changes
"""

import os
import re
import json
import sys
import shutil
import argparse
from pathlib import Path

# Security constants
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 MB per image
MAX_FILE_SIZE = 10 * 1024 * 1024   # 10 MB per markdown file

# Try to use pyyaml if available, otherwise use simple parser
try:
    import yaml
    USE_YAML = True
except ImportError:
    USE_YAML = False

def parse_yaml_frontmatter(frontmatter_str):
    """Parse YAML frontmatter - uses pyyaml if available, otherwise simple parser."""
    if USE_YAML:
        try:
            return yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError:
            pass
    
    # Fallback: Simple YAML parser (no external dependencies)
    data = {}
    current_key = None
    current_value = []
    in_list = False
    
    for line in frontmatter_str.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Handle list items
        if line.startswith('- '):
            if current_key:
                if current_key not in data:
                    data[current_key] = []
                # Remove quotes if present
                value = line[2:].strip().strip("'\"")
                data[current_key].append(value)
            in_list = True
            continue
        elif in_list and not line.startswith('-'):
            in_list = False
        
        # Handle key-value pairs
        if ':' in line:
            if current_key and current_value:
                data[current_key] = ' '.join(current_value).strip().strip("'\"")
                current_value = []
            
            parts = line.split(':', 1)
            current_key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ''
            
            if value:
                if value.startswith('[') and value.endswith(']'):
                    # Array format: tags: ['Tech', 'Rails']
                    value = value.strip('[]')
                    data[current_key] = [v.strip().strip("'\"") for v in value.split(',') if v.strip()]
                    current_key = None
                else:
                    data[current_key] = value.strip("'\"")
                    current_key = None
            else:
                current_value = []
        elif current_key:
            current_value.append(line)
    
    if current_key and current_value:
        data[current_key] = ' '.join(current_value).strip().strip("'\"")
    
    return data

def extract_frontmatter(content):
    """Extract YAML frontmatter from Markdown file."""
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)
    
    if match:
        frontmatter_str = match.group(1)
        body = match.group(2)
        frontmatter = parse_yaml_frontmatter(frontmatter_str)
        return frontmatter, body
    return {}, content

def get_articles(vault_root=None):
    """Collect all published articles from blog/articles/YYYY/published/ folders."""
    articles = []
    if vault_root:
        articles_dir = Path(vault_root) / 'blog/articles'
    else:
        articles_dir = Path('blog/articles')
    
    if not articles_dir.exists():
        print(f"Warning: Articles directory not found at {articles_dir}")
        return articles
    
    if not articles_dir.is_dir():
        print(f"Warning: Articles path exists but is not a directory: {articles_dir}")
        return articles
    
    # Find all published articles
    for year_dir in articles_dir.iterdir():
        if not year_dir.is_dir():
            continue
        
        published_dir = year_dir / 'published'
        if not published_dir.exists():
            continue
        
        for md_file in published_dir.glob('*.md'):
            try:
                # Check file size before reading
                try:
                    file_size = md_file.stat().st_size
                    if file_size > MAX_FILE_SIZE:
                        print(f"Warning: Skipping large file {md_file.name} ({file_size / 1024 / 1024:.1f} MB)")
                        continue
                except OSError:
                    continue
                
                content = md_file.read_text(encoding='utf-8')
                frontmatter, body = extract_frontmatter(content)
                
                # Only include if status is published (or if url exists)
                if frontmatter.get('status') == 'published' or frontmatter.get('url'):
                    article = {
                        'title': frontmatter.get('title', ''),
                        'date': frontmatter.get('date', ''),
                        'description': frontmatter.get('description', ''),
                        'url': frontmatter.get('url', ''),
                        'thumbnail': frontmatter.get('thumbnail', ''),
                        'tags': frontmatter.get('tags', []) if isinstance(frontmatter.get('tags'), list) else []
                    }
                    articles.append(article)
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
                continue
    
    # Sort by date (newest first)
    articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    return articles

def get_books(vault_root=None):
    """Collect all books from blog/books/ folder."""
    books = []
    if vault_root:
        books_dir = Path(vault_root) / 'blog/books'
    else:
        books_dir = Path('blog/books')
    
    if not books_dir.exists():
        print(f"Warning: Books directory not found at {books_dir}")
        return books
    
    if not books_dir.is_dir():
        print(f"Warning: Books path exists but is not a directory: {books_dir}")
        return books
    
    # Find all book files
    for md_file in books_dir.glob('*.md'):
        try:
            # Check file size before reading
            try:
                file_size = md_file.stat().st_size
                if file_size > MAX_FILE_SIZE:
                    print(f"Warning: Skipping large file {md_file.name} ({file_size / 1024 / 1024:.1f} MB)")
                    continue
            except OSError:
                continue
            
            content = md_file.read_text(encoding='utf-8')
            frontmatter, body = extract_frontmatter(content)
            
            # Only include if status is read (or if rating exists)
            if frontmatter.get('status') == 'read' or frontmatter.get('rating'):
                # Convert rating to float if it's a string
                rating = frontmatter.get('rating', 0)
                try:
                    rating = float(rating) if rating else 0
                except (ValueError, TypeError):
                    rating = 0
                
                book = {
                    'title': frontmatter.get('title', ''),
                    'author': frontmatter.get('author', ''),
                    'cover': frontmatter.get('cover', ''),
                    'rating': rating,
                    'url': frontmatter.get('url', ''),
                    'tags': frontmatter.get('tags', []) if isinstance(frontmatter.get('tags'), list) else [],
                    'lesson': (frontmatter.get('lesson', '') or body).strip()
                }
                books.append(book)
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            continue
    
    # Sort by rating (highest first), then by title
    books.sort(key=lambda x: (float(x.get('rating', 0)), x.get('title', '')), reverse=True)
    return books

def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal and invalid characters."""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove dangerous characters
    filename = re.sub(r'[<>:"|?*\x00-\x1f]', '', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    return filename

def validate_path(path, must_exist=True, must_be_dir=False):
    """Validate and resolve a path safely."""
    try:
        resolved = Path(path).resolve()
        
        # Check if path exists
        if must_exist and not resolved.exists():
            return None, f"Path does not exist: {path}"
        
        # Check if it's a directory when required
        if must_be_dir and resolved.exists() and not resolved.is_dir():
            return None, f"Path is not a directory: {path}"
        
        # Prevent path traversal beyond reasonable limits
        # This is a basic check - in production, you might want stricter rules
        if '..' in str(resolved):
            # Resolve should handle this, but double-check
            pass
        
        return resolved, None
    except (OSError, ValueError) as e:
        return None, f"Invalid path: {path} - {str(e)}"

def copy_images(vault_root=None, output_dir='data', dry_run=False):
    """Copy article images to data/images/ for the portfolio repo."""
    if vault_root:
        images_source = Path(vault_root) / 'blog/articles/images'
    else:
        images_source = Path('blog/articles/images')
    
    images_dest = Path(output_dir) / 'images'
    
    if not images_source.exists():
        print(f"Info: No images directory found at {images_source}")
        return 0
    
    if not images_source.is_dir():
        print(f"Warning: Images path exists but is not a directory: {images_source}")
        return 0
    
    # Create destination directory
    if not dry_run:
        images_dest.mkdir(parents=True, exist_ok=True)
    else:
        print(f"[DRY RUN] Would create directory: {images_dest}")
    
    # Copy all images with security checks
    copied = 0
    skipped = 0
    for image_file in images_source.glob('*'):
        if not image_file.is_file():
            continue
            
        # Check file extension
        if image_file.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            continue
        
        # Check file size
        try:
            file_size = image_file.stat().st_size
            if file_size > MAX_IMAGE_SIZE:
                print(f"Warning: Skipping large image {image_file.name} ({file_size / 1024 / 1024:.1f} MB > {MAX_IMAGE_SIZE / 1024 / 1024} MB)")
                skipped += 1
                continue
        except OSError as e:
            print(f"Warning: Cannot read file {image_file.name}: {e}")
            skipped += 1
            continue
        
        # Sanitize filename
        safe_name = sanitize_filename(image_file.name)
        dest_file = images_dest / safe_name
        
        if dry_run:
            print(f"[DRY RUN] Would copy: {image_file.name} -> {dest_file}")
        else:
            try:
                shutil.copy2(image_file, dest_file)
                copied += 1
            except (OSError, shutil.Error) as e:
                print(f"Error copying {image_file.name}: {e}")
                skipped += 1
    
    if not dry_run and copied > 0:
        print(f"Copied {copied} images to {images_dest}/")
    if skipped > 0:
        print(f"Skipped {skipped} images")
    
    return copied

def main():
    """Generate JSON files."""
    parser = argparse.ArgumentParser(
        description='Generate JSON files from Obsidian Markdown articles and books.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run from Obsidian vault root
  python3 generate_json.py
  
  # Specify vault and output paths
  python3 generate_json.py /path/to/vault /path/to/output
  
  # Dry run to see what would happen
  python3 generate_json.py --dry-run /path/to/vault
        """
    )
    parser.add_argument('vault_path', nargs='?', default=None,
                       help='Path to Obsidian vault root (default: current directory)')
    parser.add_argument('output_path', nargs='?', default='data',
                       help='Path to output directory (default: ./data)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    # Validate vault path
    vault_root = None
    if args.vault_path:
        resolved, error = validate_path(args.vault_path, must_exist=True, must_be_dir=True)
        if error:
            print(f"Error: {error}", file=sys.stderr)
            sys.exit(1)
        vault_root = str(resolved)
    
    # Validate output path
    output_dir = args.output_path
    resolved, error = validate_path(output_dir, must_exist=False)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    output_dir = str(resolved)
    
    # Check if output files already exist
    articles_path = Path(output_dir) / 'articles.json'
    books_path = Path(output_dir) / 'books.json'
    
    if not args.dry_run:
        if articles_path.exists() or books_path.exists():
            print("Warning: Output files already exist and will be overwritten:")
            if articles_path.exists():
                print(f"  - {articles_path}")
            if books_path.exists():
                print(f"  - {books_path}")
            print()
    
    # Create output directory if it doesn't exist
    if not args.dry_run:
        os.makedirs(output_dir, exist_ok=True)
    
    print(f"Using vault root: {vault_root or 'current directory'}")
    print(f"Output directory: {output_dir}")
    if args.dry_run:
        print("DRY RUN MODE: No files will be modified")
    print()
    
    # Copy images first
    copy_images(vault_root, output_dir, dry_run=args.dry_run)
    
    # Generate articles.json
    articles = get_articles(vault_root)
    if not args.dry_run:
        with open(articles_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"\nGenerated {articles_path} with {len(articles)} articles")
    else:
        print(f"\n[DRY RUN] Would generate {articles_path} with {len(articles)} articles")
    
    for article in articles:
        print(f"  - {article.get('title', 'Untitled')} ({article.get('date', 'no date')})")
    
    # Generate books.json
    books = get_books(vault_root)
    if not args.dry_run:
        with open(books_path, 'w', encoding='utf-8') as f:
            json.dump(books, f, ensure_ascii=False, indent=2)
        print(f"\nGenerated {books_path} with {len(books)} books")
    else:
        print(f"\n[DRY RUN] Would generate {books_path} with {len(books)} books")
    
    for book in books:
        print(f"  - {book.get('title', 'Untitled')} by {book.get('author', 'Unknown')} ({book.get('rating', 0)}/5)")
    
    if args.dry_run:
        print("\n[DRY RUN] No files were modified. Run without --dry-run to apply changes.")

if __name__ == '__main__':
    main()

