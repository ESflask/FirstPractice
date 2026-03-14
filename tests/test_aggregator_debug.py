import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path to import app modules
sys.path.append(os.getcwd())

load_dotenv()

from app.services.aggregator import get_translated_articles

def test_aggregator():
    print("--- Testing get_translated_articles ---")
    articles = get_translated_articles(query="Apple", page_size=5, lang="ja")
    print(f"Total articles returned: {len(articles)}")
    for i, a in enumerate(articles, 1):
        print(f"{i}. {a.get('title_ja')} ({a.get('source')})")

if __name__ == "__main__":
    test_aggregator()
