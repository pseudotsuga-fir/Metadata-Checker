#!/usr/bin/env python3
"""
Metadata Scraper Script

This script takes a sitemap XML URL and scrapes metadata from the specified number of pages.
It checks canonical URLs and formats output with match status.
"""

import argparse
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time
import sys
from typing import List, Dict, Optional
from datetime import datetime
import re
import os


def parse_sitemap(sitemap_url: str) -> List[str]:
    """
    Parse XML sitemap and extract URLs.
    
    Args:
        sitemap_url: URL to the sitemap XML file
        
    Returns:
        List of URLs from the sitemap
    """
    try:
        # Use more standard headers that are less likely to be blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(sitemap_url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        
        # Handle different sitemap namespaces
        namespaces = {
            'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'news': 'http://www.google.com/schemas/sitemap-news/0.9',
            'image': 'http://www.google.com/schemas/sitemap-image/1.1'
        }
        
        urls = []
        
        # Try different namespace approaches
        for namespace in namespaces.values():
            try:
                url_elements = root.findall(f'.//{{{namespace}}}url')
                if url_elements:
                    for url_elem in url_elements:
                        loc_elem = url_elem.find(f'{{{namespace}}}loc')
                        if loc_elem is not None and loc_elem.text:
                            urls.append(loc_elem.text.strip())
                    break
            except Exception:
                continue
        
        # Fallback: try without namespace
        if not urls:
            url_elements = root.findall('.//url')
            for url_elem in url_elements:
                loc_elem = url_elem.find('loc')
                if loc_elem is not None and loc_elem.text:
                    urls.append(loc_elem.text.strip())
        
        return urls
        
    except requests.RequestException as e:
        print(f"Error fetching sitemap: {e}")
        print(f"Response status code: {getattr(e.response, 'status_code', 'N/A')}")
        print(f"Response headers: {getattr(e.response, 'headers', 'N/A')}")
        sys.exit(1)
    except ET.ParseError as e:
        print(f"Error parsing XML sitemap: {e}")
        sys.exit(1)


def extract_metadata(url: str) -> Dict[str, str]:
    """
    Extract metadata from a webpage.
    
    Args:
        url: URL of the page to scrape
        
    Returns:
        Dictionary containing metadata
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        metadata = {
            'url': url,
            'canonical': '',
            'title': '',
            'description': ''
        }
        
        # Extract canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            metadata['canonical'] = canonical['href']
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Extract description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            metadata['description'] = desc_tag['content'].strip()
        
        return metadata
        
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return {
            'url': url,
            'canonical': '',
            'title': 'ERROR: Could not fetch page',
            'description': ''
        }


def check_canonical_match(url: str, canonical: str) -> bool:
    """
    Check if canonical URL matches the original URL domain.
    
    Args:
        url: Original URL
        canonical: Canonical URL from page
        
    Returns:
        True if domains match, False otherwise
    """
    if not canonical:
        return False
    
    try:
        original_domain = urlparse(url).netloc
        canonical_domain = urlparse(canonical).netloc
        
        return original_domain == canonical_domain
    except Exception:
        return False


def format_output(metadata: Dict[str, str]) -> str:
    """
    Format metadata output according to specification.
    
    Args:
        metadata: Dictionary containing page metadata
        
    Returns:
        Formatted string output
    """
    url = metadata['url']
    canonical = metadata['canonical']
    title = metadata['title']
    description = metadata['description']
    
    # Check if canonical matches
    match_status = "✓" if check_canonical_match(url, canonical) else "FAIL"
    
    # Format output
    output = f"{url}\n"
    output += "=" * len(url) + "\n"
    output += f"match {match_status}\n"
    output += f"canonical: {canonical}\n"
    output += f"title: {title}\n"
    output += f"desc: {description}\n"
    
    return output


def generate_filename(sitemap_url: str) -> str:
    """
    Generate filename with domain and timestamp.
    
    Args:
        sitemap_url: URL to extract domain from
        
    Returns:
        Generated filename with output folder path
    """
    try:
        # Extract domain from sitemap URL
        parsed_url = urlparse(sitemap_url)
        domain = parsed_url.netloc
        
        # Clean domain name (remove www. if present)
        domain = re.sub(r'^www\.', '', domain)
        
        # Replace dots and other special characters with underscores
        domain = re.sub(r'[^\w\-]', '_', domain)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"output/{domain}_metadata_check_{timestamp}.txt"
        
    except Exception:
        # Fallback if domain extraction fails
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"output/metadata_check_{timestamp}.txt"


def main():
    """Main function to run the metadata scraper."""
    parser = argparse.ArgumentParser(
        description='Scrape metadata from pages listed in a sitemap XML file'
    )
    parser.add_argument(
        'sitemap_url',
        help='URL to the sitemap XML file'
    )
    parser.add_argument(
        'page_count',
        type=int,
        help='Number of pages to scrape'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output file name (default: auto-generated with domain and timestamp)'
    )
    parser.add_argument(
        '--delay',
        '-d',
        type=float,
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    
    args = parser.parse_args()
    
    # Generate filename if not provided
    if args.output:
        output_filename = args.output
    else:
        output_filename = generate_filename(args.sitemap_url)
    
    print(f"Fetching sitemap from: {args.sitemap_url}")
    urls = parse_sitemap(args.sitemap_url)
    
    if not urls:
        print("No URLs found in sitemap")
        sys.exit(1)
    
    print(f"Found {len(urls)} URLs in sitemap")
    
    # Limit to requested number of pages
    urls_to_scrape = urls[:args.page_count]
    
    print(f"Scraping {len(urls_to_scrape)} pages...")
    print(f"Output will be saved to: {output_filename}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Open file for writing and write in real-time
    with open(output_filename, 'w', encoding='utf-8') as f:
        for i, url in enumerate(urls_to_scrape, 1):
            print(f"Scraping {i}/{len(urls_to_scrape)}: {url}")
            
            metadata = extract_metadata(url)
            formatted_output = format_output(metadata)
            
            # Write to file immediately
            f.write(formatted_output)
            
            # Add separator line between pages (except for the last page)
            if i < len(urls_to_scrape):
                f.write('\n\n')
            
            # Flush to ensure data is written immediately
            f.flush()
            
            # Add delay between requests to be respectful
            if i < len(urls_to_scrape):
                time.sleep(args.delay)
    
    print(f"\nResults saved to: {output_filename}")
    print(f"Scraped {len(urls_to_scrape)} pages successfully")


if __name__ == "__main__":
    main()
