# Metadata Scraper

A Python script that scrapes metadata from pages listed in a sitemap XML file.

## Features

- Parses XML sitemaps and extracts URLs
- Scrapes metadata (title, description, canonical URL) from web pages
- Checks if canonical URLs match the original domain
- Formats output with match status (✓ or FAIL)
- Respectful scraping with configurable delays
- Handles various sitemap formats and namespaces

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python main.py <sitemap_url> <page_count>
```

### Examples

```bash
# Scrape 10 pages from a sitemap
python main.py https://example.com/sitemap.xml 10

# Scrape 5 pages with custom output file
python main.py https://example.com/sitemap.xml 5 --output my_results.txt

# Scrape with 2-second delay between requests
python main.py https://example.com/sitemap.xml 10 --delay 2.0
```

### Command Line Arguments

- `sitemap_url`: URL to the sitemap XML file (required)
- `page_count`: Number of pages to scrape (required)
- `--output, -o`: Output file name (default: metadata_output.txt)
- `--delay, -d`: Delay between requests in seconds (default: 1.0)

## Output Format

The script creates a file with metadata formatted as follows:

```
https://testsite.com/blog-page
=======================
match ✓
canonical: https://testsite.com/blog-page
title: Welcome to Page
desc: Hello...

https://testsite.com/another-page
===============================
match FAIL
canonical: https://othersite.com/another-page
title: Another Page Title
desc: Another page description...
```

### Match Status

- `✓`: Canonical URL domain matches the original URL domain
- `FAIL`: Canonical URL domain does not match or no canonical URL found

## Error Handling

- The script handles network errors gracefully
- Invalid XML sitemaps are reported with clear error messages
- Pages that cannot be fetched are marked with an error message
- The script continues processing even if individual pages fail

## Notes

- The script includes a User-Agent header to avoid being blocked
- A default 1-second delay is added between requests to be respectful to servers
- The script supports various sitemap namespaces and formats
- All output is saved to a UTF-8 encoded text file
