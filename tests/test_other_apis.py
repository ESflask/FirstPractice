import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_gnews(query):
    API_KEY = os.getenv("GNEWS_API_KEY")
    BASE_URL = "https://gnews.io/api/v4/search"
    print(f"\n--- Testing GNews with query: {query} ---")
    params = {
        "q": query,
        "apikey": API_KEY,
        "max": 3
    }
    resp = requests.get(BASE_URL, params=params)
    print(f"Status Code: {resp.status_code}")
    data = resp.json()
    articles = data.get('articles', [])
    print(f"Articles returned: {len(articles)}")
    for a in articles:
        print(f"- {a.get('title')}")

def test_newsdata(query):
    API_KEY = os.getenv("NEWSDATA_KEY")
    BASE_URL = "https://newsdata.io/api/1/news"
    print(f"\n--- Testing NewsData.io with query: {query} ---")
    params = {
        "q": query,
        "apikey": API_KEY,
        "size": 3
    }
    resp = requests.get(BASE_URL, params=params)
    print(f"Status Code: {resp.status_code}")
    data = resp.json()
    articles = data.get('results', [])
    print(f"Articles returned: {len(articles)}")
    for a in articles:
        print(f"- {a.get('title')}")

if __name__ == "__main__":
    test_gnews("Apple")
    test_newsdata("Apple")
