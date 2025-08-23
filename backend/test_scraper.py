
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import extract_article_content
import time

def test_scraper():
   
    # Test URLs with different website structures
    test_urls = [
        "https://example.com",  
        "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "https://httpbin.org/html", 
    ]
    
    print("Testing web scraper functionality...")
    print("=" * 50)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}: {url}")
        print("-" * 30)
        
        try:
            result = extract_article_content(url)
            
            if result:
                print(f"✅ SUCCESS")
                print(f"Title: {result['title'][:100]}...")
                print(f"Content length: {len(result['content'])} characters")
                print(f"Word count: {len(result['content'].split())} words")
                print(f"Final URL: {result['url']}")
                
               
                preview = result['content'][:200].replace('\n', ' ')
                print(f"Preview: {preview}...")
                
            else:
                print(f"❌ FAILED - No content extracted")
                
        except Exception as e:
            print(f"❌ ERROR - {str(e)}")
        
        
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("Scraper testing completed")

def test_edge_cases():
    """Test edge cases and error handling"""
    
    print("\nTesting edge cases...")
    print("=" * 50)
    
    edge_cases = [
        ("Invalid URL", "not-a-url"),
        ("Non-existent domain", "https://this-domain-should-not-exist-12345.com"),
        ("Empty URL", ""),
        ("None input", None),
    ]
    
    for case_name, url in edge_cases:
        print(f"\nTesting: {case_name}")
        print(f"URL: {url}")
        
        try:
            if url is None:
                
                print("❌ EXPECTED - None input not allowed")
                continue
                
            result = extract_article_content(url)
            
            if result is None:
                print("✅ EXPECTED - Correctly handled invalid input")
            else:
                print(f"⚠️  UNEXPECTED - Got result: {result}")
                
        except Exception as e:
            print(f"✅ EXPECTED - Error handled: {str(e)}")

if __name__ == "__main__":
    test_scraper()
    test_edge_cases()
