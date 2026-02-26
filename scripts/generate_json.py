#!/usr/bin/env python3
import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

def parse_yaml_frontmatter(frontmatter_str: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for line in frontmatter_str.split('\n'):
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip().strip("'\"")
            if value.startswith('[') and value.endswith(']'):
                data[key] = [v.strip().strip("'\"") for v in value.strip('[]').split(',') if v.strip()]
            else:
                data[key] = value
    return data

def extract_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        return parse_yaml_frontmatter(match.group(1)), match.group(2)
    return {}, content

def get_articles(vault_path: Path) -> List[Dict[str, Any]]:
    articles = []
    # Logic to match your Gitea structure: blog/articles/YYYY/published/
    blog_dir = vault_path / 'blog' / 'articles'
    if not blog_dir.exists():
        return articles

    for year_dir in blog_dir.iterdir():
        if not year_dir.is_dir(): continue
        pub_dir = year_dir / 'published'
        if not pub_dir.exists(): continue
        
        for md_file in pub_dir.glob('*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                fm, _ = extract_frontmatter(content)
                if fm.get('status') == 'published' or fm.get('url'):
                    # Match your "Image in blog section" requirement
                    # The thumbnail path is now relative to the blog folder
                    articles.append({
                        'title': fm.get('title', md_file.stem),
                        'date': fm.get('date', ''),
                        'description': fm.get('description', ''),
                        'url': fm.get('url', ''),
                        'thumbnail': fm.get('cover_image', fm.get('thumbnail', '')),
                        'tags': fm.get('tags', [])
                    })
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
    
    articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    return articles

def main():
    # Accept arguments from the Gitea Action
    vault_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('.')
    
    articles = get_articles(vault_path)
    
    os.makedirs(output_path / 'data', exist_ok=True)
    with open(output_path / 'data' / 'articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(articles)} articles in {output_path}/data/articles.json")

if __name__ == '__main__':
    main()
