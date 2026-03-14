import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWSAPI_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def test_newsapi(query):
    print(f"\n--- Testing NewsAPI with query: {query} ---")
    params = {
        "q": query,
        "pageSize": 3,
        "apiKey": API_KEY,
    }
    
    resp = requests.get(BASE_URL, params=params)
    print(f"Status Code: {resp.status_code}")
    data = resp.json()
    print(f"Total Results: {data.get('totalResults')}")
    articles = data.get('articles', [])
    print(f"Articles returned: {len(articles)}")
    for a in articles:
        print(f"- {a.get('title')}")

if __name__ == "__main__":
    test_newsapi("Apple")
    test_newsapi('"Apple"')
