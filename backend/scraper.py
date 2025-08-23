import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import re
import time
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    text = re.sub(r'\s+', ' ', text)
    
    text = re.sub(r'[^\w\s.,!?;:()\-\'"]+', '', text)
    
   
    text = re.sub(r'\.{3,}', '...', text)
    text = re.sub(r'-{2,}', '--', text)
    
    return text.strip()

def get_headers() -> Dict[str, str]:
    """Get realistic browser headers for requests"""
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def remove_unwanted_elements(soup: BeautifulSoup) -> None:
    """Remove unwanted HTML elements"""
    unwanted_tags = [
        'script', 'style', 'nav', 'header', 'footer', 'aside', 
        'advertisement', 'ads', 'sidebar', 'menu', 'social',
        'comment', 'comments', 'popup', 'modal', 'overlay',
        'cookie', 'newsletter', 'subscription'
    ]
    
    # Remove by tag name
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove by class/id patterns
    unwanted_patterns = [
        'nav', 'menu', 'sidebar', 'footer', 'header', 'ad', 'advertisement',
        'social', 'share', 'comment', 'popup', 'modal', 'cookie',
        'newsletter', 'subscription', 'related', 'recommended'
    ]
    
    for pattern in unwanted_patterns:
        # Remove by class
        for element in soup.find_all(attrs={'class': re.compile(pattern, re.I)}):
            element.decompose()
        # Remove by id
        for element in soup.find_all(attrs={'id': re.compile(pattern, re.I)}):
            element.decompose()

def extract_title(soup: BeautifulSoup) -> str:
    """Extract title with multiple fallback so we can have more robustness"""
    title_selectors = [
        'h1.title',
        'h1.post-title', 
        'h1.entry-title',
        'h1.article-title',
        '.title h1',
        'article h1',
        'h1',
        'title'
    ]
    
    for selector in title_selectors:
        element = soup.select_one(selector)
        if element:
            title = element.get_text().strip()
            if title and len(title) > 5:  # no super short titles
                return clean_text(title)
    
    return "Untitled"

def extract_content(soup: BeautifulSoup) -> str:
    """Extract main content with improved selectors"""
   
    content_selectors = [
        'article .content',
        'article .post-content',
        'article .entry-content', 
        'article .article-content',
        'article .article-body',
        '.post-content',
        '.entry-content',
        '.article-content',
        '.article-body',
        '.content',
        'article',
        '[role="main"]',
        'main .content',
        'main',
        '.main-content',
        '#content',
        '#main-content'
    ]
    
    for selector in content_selectors:
        content_element = soup.select_one(selector)
        if content_element:
          
            paragraphs = content_element.find_all('p')
            if paragraphs:
                content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            else:
                content = content_element.get_text(separator=' ', strip=True)
            
            content = clean_text(content)
            
          
            if len(content) > 200 and len(content.split()) > 50:
                return content
    

    body = soup.find('body')
    if body:
       
        for nav in body.find_all(['nav', 'header', 'footer', 'aside']):
            nav.decompose()
        
        content = body.get_text(separator=' ', strip=True)
        content = clean_text(content)
        return content
    
    return ""

def extract_article_content(url: str, retry_count: int = 2) -> Optional[Dict[str, str]]:
   
    if not is_valid_url(url):
        logger.error(f"Invalid URL format: {url}")
        return None
    
    for attempt in range(retry_count + 1):
        try:
            logger.info(f"Attempting to scrape {url} (attempt {attempt + 1})")
            
            session = requests.Session()
            session.headers.update(get_headers())
            
            # Add delay 
            if attempt > 0:
                time.sleep(2)
            
            response = session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.error(f"Invalid content type: {content_type}")
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            remove_unwanted_elements(soup)
            
            # Extract title and content
            title = extract_title(soup)
            content = extract_content(soup)
            
            # Validation
            if not content or len(content) < 100:
                logger.warning(f"Content too short ({len(content)} chars) for {url}")
                if attempt < retry_count:
                    continue
                return None
            
            if len(content.split()) < 20:
                logger.warning(f"Content has too few words ({len(content.split())} words) for {url}")
                if attempt < retry_count:
                    continue
                return None
            
            logger.info(f"Successfully scraped {url}: {len(content)} chars, {len(content.split())} words")
            
            return {
                'title': title,
                'content': content,
                'url': response.url  # Use final URL after redirects
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout scraping {url} (attempt {attempt + 1})")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error scraping {url} (attempt {attempt + 1})")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} scraping {url}")
            if e.response.status_code in [404, 403, 401]:
                break  # Don't retry for these errors
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
    
    logger.error(f"Failed to scrape {url} after {retry_count + 1} attempts")
    return None
