#!/usr/bin/env python
import sys
import traceback
from app import get_translated_articles

print("Testing get_translated_articles function...")
print("=" * 50)

try:
    articles = get_translated_articles(query="Apple", page_size=2)
    print(f"\nSuccess! Got {len(articles)} articles")
    
    if articles:
        print("\nFirst article:")
        for key, value in articles[0].items():
            if isinstance(value, str) and len(value) > 100:
                print(f"  {key}: {value[:100]}...")
            else:
                print(f"  {key}: {value}")
    else:
        print("\nNo articles returned (empty list)")
        
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
