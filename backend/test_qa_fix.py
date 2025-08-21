#!/usr/bin/env python3
"""
Quick test script to verify Q&A fix
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_qa_fix():
    """Test Q&A with existing user data"""
    
    # Create a new test user
    import time
    user_data = {
        "email": f"test_qa_{int(time.time())}@example.com",
        "password": "testpassword123"
    }
    
    print("Testing Q&A fix...")
    print("=" * 40)
    
    # Try to login with the test user
    print("\n1. Attempting login...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=user_data)
        if response.status_code == 200:
            login_data = response.json()
            access_token = login_data["access_token"]
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            
            # If login fails, try to register
            print("\n1b. Trying registration...")
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 200:
                login_data = response.json()
                access_token = login_data["access_token"]
                print("✅ Registration successful")
            else:
                print(f"❌ Registration also failed: {response.status_code}")
                return
                
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return
    
    # Set up headers for authenticated requests
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # First add an article to test with
    print("\n2. Adding test article...")
    article_data = {
        "url": "https://httpbin.org/html",
        "tags": "test,demo"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/articles", json=article_data, headers=headers)
        if response.status_code == 200:
            article = response.json()
            print(f"✅ Article added: {article['title'][:50]}...")
        else:
            print(f"❌ Article addition failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Article addition error: {e}")
        return
    
    # Test Q&A endpoint
    print("\n3. Testing Q&A endpoint...")
    qa_data = {
        "question": "What is this about?",
        "limit": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/qa", json=qa_data, headers=headers)
        if response.status_code == 200:
            qa_result = response.json()
            print("✅ Q&A request successful")
            print(f"Answer: {qa_result.get('answer', 'No answer')[:200]}...")
            
            if 'sources' in qa_result:
                print(f"Sources found: {len(qa_result['sources'])}")
                for i, source in enumerate(qa_result['sources'], 1):
                    print(f"  {i}. {source.get('title', 'Unknown')} (similarity: {source.get('similarity_score', 0):.3f})")
            else:
                print("No sources in response")
                
            if 'context_used' in qa_result:
                print(f"Context chunks used: {qa_result['context_used']}")
        else:
            print(f"❌ Q&A failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Q&A error: {e}")
    
    print("\n" + "=" * 40)
    print("Q&A fix test completed")

if __name__ == "__main__":
    test_qa_fix()