#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY")
print(f"Using API Key: {API_KEY[:10]}...")

url = "https://newsapi.org/v2/everything"
params = {
    "q": "Apple",
    "sortBy": "relevancy",
    "pageSize": 3,
    "apiKey": API_KEY,
}

print(f"\nMaking request to: {url}")
print(f"Parameters: q={params['q']}, pageSize={params['pageSize']}")

try:
    resp = requests.get(url, params=params, timeout=10)
    print(f"\nStatus Code: {resp.status_code}")
    
    if resp.ok:
        data = resp.json()
        print(f"Total Results: {data.get('totalResults', 0)}")
        articles = data.get('articles', [])
        print(f"Articles returned: {len(articles)}")
        
        if articles:
            print("\nFirst article:")
            print(f"  Title: {articles[0].get('title', 'N/A')}")
            print(f"  Source: {articles[0].get('source', {}).get('name', 'N/A')}")
        else:
            print("\nNo articles returned!")
            print(f"Full response: {data}")
    else:
        print(f"Error response:")
        try:
            error_data = resp.json()
            print(f"  Status: {error_data.get('status')}")
            print(f"  Code: {error_data.get('code')}")
            print(f"  Message: {error_data.get('message')}")
        except:
            print(f"  Raw: {resp.text[:500]}")
            
except Exception as e:
    print(f"\nException occurred: {type(e).__name__}: {e}")
    sys.exit(1)
