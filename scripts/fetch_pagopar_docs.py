#!/usr/bin/env python3
"""Fetches PagoPar API knowledge base articles and stores them locally."""
from __future__ import annotations

import json
import pathlib
import re
from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

PORTAL_ID = "edbsn090a928882b7e5dc61097ae8f267763b869c98670cc3d3f0899a42e01f005cf6"
BASE_URL = "https://soporte.pagopar.com/portal/api/kbArticles"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) PagoParDocsBot/1.0",
    "Accept": "application/json",
}

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ARTICLE_DIR = ROOT / "docs" / "source" / "articles"


def fetch_json(url: str, **params) -> dict:
    response = requests.get(url, headers=HEADERS, params={"portalId": PORTAL_ID, **params})
    response.raise_for_status()
    return response.json()


def clean_filename(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-") or "article"


@dataclass
class Article:
    id: str
    title: str
    permalink: str
    summary: str
    category: str
    locale: str
    html: str

    def to_markdown(self) -> str:
        """Convert the HTML answer into Markdown."""
        markdown = md(
            self.html,
            heading_style="ATX",
            strip=["span"],
        )
        return markdown.strip()

    def to_text(self) -> str:
        soup = BeautifulSoup(self.html, "html.parser")
        return soup.get_text("\n", strip=True)


def collect_articles() -> List[Article]:
    listing = fetch_json(BASE_URL)["data"]
    articles: List[Article] = []
    for item in listing:
        detail = fetch_json(f"{BASE_URL}/{item['id']}")
        articles.append(
            Article(
                id=item["id"],
                title=detail["title"],
                permalink=detail["permalink"],
                summary=detail.get("summary", ""),
                category=detail.get("category", {}).get("name", ""),
                locale=detail.get("locale", ""),
                html=detail.get("answer", ""),
            )
        )
    return articles


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)

    articles = collect_articles()
    payload = [
        {
            "id": a.id,
            "title": a.title,
            "permalink": a.permalink,
            "summary": a.summary,
            "category": a.category,
            "locale": a.locale,
            "content_html": a.html,
            "content_markdown": a.to_markdown(),
            "content_text": a.to_text(),
        }
        for a in articles
    ]

    (DATA_DIR / "pagopar_articles.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    for article in articles:
        filename = clean_filename(article.permalink or article.title)
        path = ARTICLE_DIR / f"{filename}.md"
        header = f"# {article.title}\n\n> Categoría: {article.category} | Idioma: {article.locale}\n\n"
        path.write_text(header + article.to_markdown() + "\n", encoding="utf-8")

    print(f"Fetched {len(articles)} articles")
    print(f"Saved JSON to {(DATA_DIR / 'pagopar_articles.json').relative_to(ROOT)}")
    print(f"Saved Markdown files to {ARTICLE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
