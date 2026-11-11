"""seo-audit: a small command-line SEO checker for a single web page.

Usage:
    python seo_audit.py https://example.com
    python seo_audit.py page.html          # works on a local file too
    python seo_audit.py https://example.com --json
"""
import argparse
import json
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

TITLE_RANGE = (30, 60)
DESC_RANGE = (70, 160)


def load_html(source: str) -> str:
    path = Path(source)
    if path.exists():
        return path.read_text(encoding="utf-8")
    response = requests.get(source, timeout=15, headers={"User-Agent": "seo-audit/1.0"})
    response.raise_for_status()
    return response.text


def check_range(name: str, text: str, low: int, high: int) -> dict:
    if not text:
        return {"check": name, "status": "fail", "detail": "missing"}
    n = len(text)
    if low <= n <= high:
        return {"check": name, "status": "pass", "detail": f"{n} characters"}
    return {"check": name, "status": "warn", "detail": f"{n} characters (ideal {low}-{high})"}


def audit(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []

    title = soup.title.get_text(strip=True) if soup.title else ""
    results.append(check_range("title", title, *TITLE_RANGE))

    meta = soup.find("meta", attrs={"name": "description"})
    description = (meta.get("content") or "").strip() if meta else ""
    results.append(check_range("meta description", description, *DESC_RANGE))

    h1s = soup.find_all("h1")
    if len(h1s) == 1:
        results.append({"check": "h1", "status": "pass", "detail": "exactly one h1"})
    else:
        results.append({"check": "h1", "status": "fail", "detail": f"{len(h1s)} h1 tags (expected 1)"})

    images = soup.find_all("img")
    missing_alt = [i for i in images if not (i.get("alt") or "").strip()]
    if missing_alt:
        results.append({"check": "image alt text", "status": "warn",
                        "detail": f"{len(missing_alt)} of {len(images)} images have no alt text"})
    else:
        results.append({"check": "image alt text", "status": "pass", "detail": f"{len(images)} images checked"})

    canonical = soup.find("link", rel="canonical")
    results.append({"check": "canonical link", "status": "pass" if canonical else "warn",
                    "detail": canonical["href"] if canonical and canonical.get("href") else "missing"})

    schema_types = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except json.JSONDecodeError:
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict) and "@type" in item:
                schema_types.append(str(item["@type"]))
    results.append({"check": "schema.org structured data",
                    "status": "pass" if schema_types else "warn",
                    "detail": ", ".join(schema_types) if schema_types else "no JSON-LD found"})

    viewport = soup.find("meta", attrs={"name": "viewport"})
    results.append({"check": "mobile viewport", "status": "pass" if viewport else "fail",
                    "detail": "present" if viewport else "missing"})
    return results


def score(results: list[dict]) -> int:
    points = {"pass": 1.0, "warn": 0.5, "fail": 0.0}
    return round(100 * sum(points[r["status"]] for r in results) / len(results))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Audit the basic on-page SEO of a URL or HTML file.")
    parser.add_argument("source", help="URL or path to a local HTML file")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    args = parser.parse_args(argv)

    results = audit(load_html(args.source))
    total = score(results)
    if args.json:
        print(json.dumps({"score": total, "results": results}, indent=2))
    else:
        icons = {"pass": "[ OK ]", "warn": "[WARN]", "fail": "[FAIL]"}
        for r in results:
            print(f"{icons[r['status']]} {r['check']}: {r['detail']}")
        print(f"\nSEO score: {total}/100")
    return 0


if __name__ == "__main__":
    sys.exit(main())
