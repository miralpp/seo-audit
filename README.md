# seo-audit

A small Python command-line tool that checks the basic on-page SEO of a web page: title and meta description length, a single `h1`, image alt text, canonical link, Schema.org (JSON-LD) structured data and the mobile viewport tag. It prints a pass/warn/fail report and a score out of 100.

I built it after doing SEO and structured-data work for a local business website, to make those checks repeatable.

## Install

```bash
pip install -r requirements.txt
```

## Usage

```bash
python seo_audit.py https://example.com
python seo_audit.py page.html
python seo_audit.py https://example.com --json
```

Example output:

```
[ OK ] title: 48 characters
[WARN] meta description: 55 characters (ideal 70-160)
[ OK ] h1: exactly one h1
[WARN] image alt text: 2 of 5 images have no alt text
[ OK ] canonical link: https://example.com/
[WARN] schema.org structured data: no JSON-LD found
[ OK ] mobile viewport: present

SEO score: 79/100
```

## Tests

```bash
pytest
```

## Ideas for next steps

- Suggest improved titles and descriptions with an open-source language model
- Crawl a whole sitemap and export a CSV report
