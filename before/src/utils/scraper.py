"""
Web scraper for legal documents from legaldesk.com
Extracts document links, content, and metadata
"""

import requests
from bs4 import BeautifulSoup
import html2text
import json
import time
from typing import List, Dict
from datetime import datetime
import os


class LegalDocumentScraper:
    """
    Scraper for extracting legal documents from legaldesk.com
    """
    
    def __init__(self, base_url: str = "https://legaldesk.com/documents", delay: float = 1.0):
        """
        Initialize the scraper
        
        Args:
            base_url: Main documents page URL
            delay: Delay between requests in seconds (rate limiting)
        """
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        
    def get_document_links(self) -> List[Dict[str, str]]:
        """
        Extract all document links from the main page
        
        Returns:
            List of dictionaries with document title and URL
        """
        print(f"Fetching document links from {self.base_url}...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Find all document links
            document_links = []
            
            # Look for links in the main content area
            # Adjust selectors based on actual website structure
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                # Filter for document pages
                if href and ('/documents/' in href or '/affidavits/' in href):
                    # Make absolute URL
                    if href.startswith('/'):
                        full_url = f"https://legaldesk.com{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    # Skip duplicates
                    if not any(d['url'] == full_url for d in document_links):
                        document_links.append({
                            'title': title or 'Untitled Document',
                            'url': full_url,
                            'category': self._extract_category(full_url)
                        })
            
            print(f"Found {len(document_links)} document links")
            return document_links
            
        except Exception as e:
            print(f"Error fetching document links: {e}")
            return []
    
    def _extract_category(self, url: str) -> str:
        """Extract document category from URL"""
        if '/affidavits/' in url:
            return 'Affidavit'
        elif '/rental-agreement' in url:
            return 'Rental Agreement'
        elif '/power-of-attorney' in url:
            return 'Power of Attorney'
        elif '/will' in url:
            return 'Will'
        elif '/documents/' in url:
            return 'Legal Document'
        return 'Other'
    
    def scrape_document(self, url: str, title: str) -> Dict:
        """
        Scrape content from a single document page
        
        Args:
            url: Document URL
            title: Document title
            
        Returns:
            Dictionary with document data
        """
        try:
            print(f"Scraping: {title[:50]}...")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract main content
            # Adjust selectors based on actual website structure
            content_div = soup.find('div', class_=['content', 'main-content', 'article-content'])
            
            if not content_div:
                # Fallback: try to find main article or content area
                content_div = soup.find('article') or soup.find('main') or soup.body
            
            # Convert HTML to markdown text
            if content_div:
                content_html = str(content_div)
                content_text = self.html_converter.handle(content_html)
            else:
                content_text = ""
            
            # Extract metadata
            meta_description = soup.find('meta', attrs={'name': 'description'})
            description = meta_description.get('content', '') if meta_description else ''
            
            document_data = {
                'title': title,
                'url': url,
                'content': content_text,
                'description': description,
                'category': self._extract_category(url),
                'scraped_at': datetime.now().isoformat()
            }
            
            # Rate limiting
            time.sleep(self.delay)
            
            return document_data
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return {
                'title': title,
                'url': url,
                'content': '',
                'description': '',
                'category': 'Error',
                'scraped_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def scrape_all_documents(self, max_documents: int = None) -> List[Dict]:
        """
        Scrape all documents from the website
        
        Args:
            max_documents: Maximum number of documents to scrape (None for all)
            
        Returns:
            List of document dictionaries
        """
        # Get all document links
        document_links = self.get_document_links()
        
        if max_documents:
            document_links = document_links[:max_documents]
        
        print(f"\nScraping {len(document_links)} documents...")
        
        # Scrape each document
        documents = []
        for i, link in enumerate(document_links, 1):
            print(f"\n[{i}/{len(document_links)}] ", end='')
            doc_data = self.scrape_document(link['url'], link['title'])
            documents.append(doc_data)
        
        print(f"\n\nSuccessfully scraped {len(documents)} documents")
        return documents
    
    def save_to_json(self, documents: List[Dict], filepath: str = "scraped_documents.json"):
        """
        Save scraped documents to JSON file
        
        Args:
            documents: List of document dictionaries
            filepath: Output file path
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, ensure_ascii=False)
            
            print(f"\nSaved {len(documents)} documents to {filepath}")
            
        except Exception as e:
            print(f"Error saving to JSON: {e}")


# Example usage
if __name__ == "__main__":
    scraper = LegalDocumentScraper()
    
    # Scrape all documents
    documents = scraper.scrape_all_documents(max_documents=10)  # Limit to 10 for testing
    
    # Save to JSON
    scraper.save_to_json(documents, "data/scraped_documents.json")
