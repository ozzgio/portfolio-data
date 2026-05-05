#!/usr/bin/env python3
"""Validate published portfolio-data artifacts."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path, result: ValidationResult, *, required: bool = True) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        if required:
            result.error(f"Missing required file: {path}")
    except json.JSONDecodeError as exc:
        result.error(f"Invalid JSON in {path}: {exc}")
    return None


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_string(
    value: Any,
    field_name: str,
    item_label: str,
    result: ValidationResult,
    *,
    required: bool = True,
) -> str:
    if value is None:
        if required:
            result.error(f"{item_label}: missing `{field_name}`")
        return ""
    if not isinstance(value, str):
        result.error(f"{item_label}: `{field_name}` must be a string")
        return ""
    cleaned = value.strip()
    if required and not cleaned:
        result.error(f"{item_label}: `{field_name}` cannot be empty")
    return cleaned


def validate_tags(value: Any, item_label: str, result: ValidationResult) -> list[str]:
    if not isinstance(value, list):
        result.error(f"{item_label}: `tags` must be an array")
        return []
    tags: list[str] = []
    for index, tag in enumerate(value, start=1):
        if not isinstance(tag, str) or not tag.strip():
            result.error(f"{item_label}: `tags[{index}]` must be a non-empty string")
            continue
        tags.append(tag.strip())
    return tags


def validate_date(value: str, item_label: str, result: ValidationResult) -> None:
    if not DATE_RE.match(value):
        result.error(f"{item_label}: `date` must use YYYY-MM-DD")
        return
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        result.error(f"{item_label}: `date` is not a valid calendar date")


def validate_local_asset(value: str, images_dir: Path, field_name: str, item_label: str, result: ValidationResult) -> None:
    if is_http_url(value):
        return
    if not (images_dir / value).is_file():
        result.error(f"{item_label}: `{field_name}` points to missing image `{value}`")


def validate_articles(data: Any, images_dir: Path, result: ValidationResult) -> None:
    if not isinstance(data, list):
        result.error("articles.json must contain an array")
        return

    titles: list[str] = []
    urls: list[str] = []

    for index, item in enumerate(data, start=1):
        item_label = f"article #{index}"
        if not isinstance(item, dict):
            result.error(f"{item_label}: entry must be an object")
            continue

        title = validate_string(item.get("title"), "title", item_label, result)
        date = validate_string(item.get("date"), "date", item_label, result)
        description = validate_string(item.get("description"), "description", item_label, result)
        is_internal = item.get("source") == "internal"
        url = validate_string(item.get("url"), "url", item_label, result, required=not is_internal)
        thumbnail = validate_string(item.get("thumbnail"), "thumbnail", item_label, result)
        tags = validate_tags(item.get("tags"), item_label, result)

        if is_internal and not item.get("slug"):
            result.error(f"{item_label}: internal articles must have a `slug`")

        if title:
            titles.append(title.casefold())
        if url:
            if not is_http_url(url):
                result.error(f"{item_label}: `url` must be an absolute http/https URL")
            urls.append(url)
        if date:
            validate_date(date, item_label, result)
        if description and len(description) < 20:
            result.warn(f"{item_label}: short `description` ({len(description)} chars)")
        if thumbnail:
            validate_local_asset(thumbnail, images_dir, "thumbnail", item_label, result)
        if not tags:
            result.warn(f"{item_label}: no tags provided")

    report_duplicates(titles, "article titles", result)
    report_duplicates(urls, "article URLs", result)


def validate_books(data: Any, images_dir: Path, result: ValidationResult) -> None:
    if not isinstance(data, list):
        result.error("books.json must contain an array")
        return

    titles: list[str] = []

    for index, item in enumerate(data, start=1):
        item_label = f"book #{index}"
        if not isinstance(item, dict):
            result.error(f"{item_label}: entry must be an object")
            continue

        title = validate_string(item.get("title"), "title", item_label, result)
        author = validate_string(item.get("author"), "author", item_label, result)
        cover = validate_string(item.get("cover"), "cover", item_label, result)
        lesson = validate_string(item.get("lesson"), "lesson", item_label, result)
        tags = validate_tags(item.get("tags"), item_label, result)

        if title:
            titles.append(title.casefold())
        if item.get("url"):
            url = validate_string(item.get("url"), "url", item_label, result, required=False)
            if url and not is_http_url(url):
                result.error(f"{item_label}: `url` must be an absolute http/https URL when present")

        rating = item.get("rating")
        if not isinstance(rating, (int, float)):
            result.error(f"{item_label}: `rating` must be numeric")
        elif rating < 0 or rating > 5:
            result.error(f"{item_label}: `rating` must be between 0 and 5")

        if cover:
            validate_local_asset(cover, images_dir, "cover", item_label, result)
        if author and len(author) < 2:
            result.warn(f"{item_label}: short `author` value")
        if lesson and len(lesson) < 15:
            result.warn(f"{item_label}: short `lesson` ({len(lesson)} chars)")
        if not tags:
            result.warn(f"{item_label}: no tags provided")

    report_duplicates(titles, "book titles", result)


def report_duplicates(values: list[str], label: str, result: ValidationResult) -> None:
    duplicates = [value for value, count in Counter(values).items() if count > 1]
    for value in duplicates:
        result.error(f"Duplicate {label}: `{value}`")


def compare_mirrors(root_data: Any, mirrored_data: Any, label: str, result: ValidationResult) -> None:
    if root_data != mirrored_data:
        result.error(f"{label} root file and data mirror are out of sync")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    images_dir = repo_root / "images"
    result = ValidationResult()

    root_articles = load_json(repo_root / "articles.json", result)
    root_books = load_json(repo_root / "books.json", result)
    mirrored_articles = load_json(repo_root / "data" / "articles.json", result, required=False)
    mirrored_books = load_json(repo_root / "data" / "books.json", result, required=False)

    if images_dir.exists() and not images_dir.is_dir():
        result.error("`images/` exists but is not a directory")

    if root_articles is not None:
        validate_articles(root_articles, images_dir, result)
    if root_books is not None:
        validate_books(root_books, images_dir, result)
    if root_articles is not None and mirrored_articles is not None:
        compare_mirrors(root_articles, mirrored_articles, "articles.json", result)
    elif (repo_root / "data" / "articles.json").exists():
        result.warn("articles.json data mirror exists but could not be validated")

    if root_books is not None and mirrored_books is not None:
        compare_mirrors(root_books, mirrored_books, "books.json", result)
    elif (repo_root / "data" / "books.json").exists():
        result.warn("books.json data mirror exists but could not be validated")

    print("portfolio-data validation summary")
    if root_articles is not None:
        print(f"- articles: {len(root_articles)}")
    if root_books is not None:
        print(f"- books: {len(root_books)}")
    print(f"- warnings: {len(result.warnings)}")
    print(f"- errors: {len(result.errors)}")

    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")

    return 1 if result.errors else 0


if __name__ == "__main__":
    sys.exit(main())
