# Metadata Scraper

A Python script that scrapes metadata from pages listed in a sitemap XML file.

## Features

- Parses XML sitemaps and extracts URLs
- Scrapes metadata (title, description, canonical URL) from web pages
- Checks if canonical URLs match the original domain
- Formats output with match status (✓ or FAIL)
- **Console warnings** when canonical URLs don't match
- Respectful scraping with configurable delays
- Handles various sitemap formats and namespaces
- Auto-generates organized output files with domain and timestamp

## Installation

1. Install the required dependencies:

```bash
pip3 install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python3 main.py <sitemap_url> <page_count>
```

### Examples

```bash
# Scrape 10 pages from a sitemap
python3 main.py https://example.com/sitemap.xml 10

# Scrape 5 pages with custom output file
python3 main.py https://example.com/sitemap.xml 5 --output my_results.txt

# Scrape with 2-second delay between requests
python3 main.py https://example.com/sitemap.xml 10 --delay 2.0
```

### Command Line Arguments

- `sitemap_url`: URL to the sitemap XML file (required)
- `page_count`: Number of pages to scrape (required)
- `--output, -o`: Output file name (default: auto-generated with domain and timestamp)
- `--delay, -d`: Delay between requests in seconds (default: 1.0)

## Output Format

### Console Output

The script provides real-time feedback in the console:

```
Fetching sitemap from: https://example.com/sitemap.xml
Found 150 URLs in sitemap
Scraping 3 pages...
Output will be saved to: output/example_com_metadata_check_20250710_103424.txt
Scraping 1/3: https://example.com/page1
Scraping 2/3: https://example.com/page2
!!! CANONICAL DID NOT MATCH - https://example.com/page2
Scraping 3/3: https://example.com/page3

Results saved to: output/example_com_metadata_check_20250710_103424.txt
Scraped 3 pages successfully
```

### File Output

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

**Note**: When a canonical URL doesn't match, the script will print `!!! CANONICAL DID NOT MATCH - [URL]` to the console for immediate visibility.

## Error Handling

- The script handles network errors gracefully
- Invalid XML sitemaps are reported with clear error messages
- Pages that cannot be fetched are marked with an error message
- The script continues processing even if individual pages fail

## File Organization

- Output files are automatically saved to an `output/` folder
- Filenames include domain and timestamp: `[domain]_metadata_check_[timestamp].txt`
- The `output/` folder is automatically created if it doesn't exist
- All generated files are ignored by git (see `.gitignore`)

## Notes

- The script includes a User-Agent header to avoid being blocked
- A default 1-second delay is added between requests to be respectful to servers
- The script supports various sitemap namespaces and formats
- All output is saved to a UTF-8 encoded text file
- Real-time file writing ensures data is saved immediately as pages are processed
