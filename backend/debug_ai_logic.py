#!/usr/bin/env python3
"""
Debug script to analyze AI processing logic issues
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def debug_ai_processing():
    """Debug AI processing with detailed analysis"""
    
    print("Debugging AI Processing Logic")
    print("=" * 50)
    
    # Register a new test user
    user_data = {
        "email": f"debug_{int(time.time())}@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Add multiple articles to test various scenarios
    test_articles = [
        {
            "url": "https://httpbin.org/html",
            "tags": "literature,classic"
        },
        {
            "url": "https://example.com",
            "tags": "example,test"
        }
    ]
    
    added_articles = []
    
    print("\n1. Adding test articles...")
    for i, article_data in enumerate(test_articles, 1):
        try:
            response = requests.post(f"{BASE_URL}/articles", json=article_data, headers=headers)
            if response.status_code == 200:
                article = response.json()
                added_articles.append(article)
                print(f"   ✅ Article {i}: {article['title'][:50]}...")
                print(f"      Content length: {len(article['content'])} chars")
                print(f"      URL: {article['url']}")
            else:
                print(f"   ❌ Article {i} failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Article {i} error: {e}")
    
    if not added_articles:
        print("No articles added, cannot proceed with debugging")
        return
    
    # Test different types of queries
    test_queries = [
        {
            "question": "What is Herman Melville's Moby Dick about?",
            "expected": "Should match literature content"
        },
        {
            "question": "Tell me about blacksmith Perth",
            "expected": "Should find specific character details"
        },
        {
            "question": "What programming languages are mentioned?",
            "expected": "Should find no relevant content"
        },
        {
            "question": "What are the main themes?",
            "expected": "Should extract thematic content"
        },
        {
            "question": "Who is the author?",
            "expected": "Should identify Herman Melville"
        }
    ]
    
    print(f"\n2. Testing {len(test_queries)} different Q&A scenarios...")
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {test_case['question']} ---")
        print(f"Expected: {test_case['expected']}")
        
        qa_data = {
            "question": test_case["question"],
            "limit": 3
        }
        
        try:
            response = requests.post(f"{BASE_URL}/qa", json=qa_data, headers=headers)
            if response.status_code == 200:
                qa_result = response.json()
                
                print(f"✅ Status: Success")
                print(f"Answer: {qa_result.get('answer', 'No answer')[:150]}...")
                
                sources = qa_result.get('sources', [])
                context_used = qa_result.get('context_used', 0)
                
                print(f"Sources: {len(sources)} articles")
                print(f"Context chunks used: {context_used}")
                
                if sources:
                    for j, source in enumerate(sources, 1):
                        similarity = source.get('similarity_score', 0)
                        title = source.get('title', 'Unknown')
                        print(f"  {j}. {title[:40]}... (similarity: {similarity:.4f})")
                        
                        # Flag potential issues
                        if similarity < 0.15:
                            print(f"     ⚠️  Low similarity score - may indicate weak relevance")
                        elif similarity > 0.8:
                            print(f"     ✨ High similarity score - strong match")
                        else:
                            print(f"     ✓  Moderate similarity score - reasonable match")
                else:
                    print("  ❌ No sources found - this could indicate:")
                    print("     - Similarity threshold too high")
                    print("     - Poor embedding quality")
                    print("     - Chunking issues")
                    print("     - No relevant content")
            else:
                print(f"❌ Q&A failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Q&A error: {e}")
    
    # Test search endpoint for comparison
    print(f"\n3. Testing search endpoint for comparison...")
    
    search_queries = [
        "Herman Melville",
        "blacksmith",
        "programming",
        "themes"
    ]
    
    for query in search_queries:
        print(f"\n--- Search: '{query}' ---")
        
        search_data = {
            "query": query,
            "limit": 3
        }
        
        try:
            response = requests.post(f"{BASE_URL}/search", json=search_data, headers=headers)
            if response.status_code == 200:
                results = response.json()
                search_results = results.get('results', [])
                
                print(f"Found {len(search_results)} results")
                
                for i, result in enumerate(search_results, 1):
                    similarity = result['similarity_score']
                    title = result['article']['title']
                    print(f"  {i}. {title[:40]}... (similarity: {similarity:.4f})")
            else:
                print(f"Search failed: {response.status_code}")
        except Exception as e:
            print(f"Search error: {e}")
    
    print("\n" + "=" * 50)
    print("AI Processing Debug Analysis Complete")
    
    # Summary and recommendations
    print("\n4. Analysis Summary:")
    print("- Current similarity threshold: 0.15")
    print("- Articles added:", len(added_articles))
    print("- Test cases executed:", len(test_queries))
    print("\nPotential Issues to Look For:")
    print("1. Similarity scores consistently below 0.2 (weak embeddings)")
    print("2. No sources found for relevant queries (threshold too high)")
    print("3. Poor context retrieval (chunking issues)")
    print("4. Generic answers despite good sources (prompt issues)")

if __name__ == "__main__":
    debug_ai_processing()