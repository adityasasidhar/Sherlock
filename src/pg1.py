import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup


def search_duckduckgo(query, num_results=10):
    query = query.replace(" ", "+")
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    blocked_domains = [
        "amazon.", "flipkart.", "ebay.", "aliexpress.", "walmart.", "etsy.",  # Shopping sites
        "facebook.", "twitter.", "instagram.", "linkedin.", "tiktok.", "reddit.", "pinterest."  # Social media
    ]

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for link in soup.find_all("a", class_="result__url"):
            url = "https://" + link.text.strip()

            # Block shopping and social media sites
            if any(blocked in url for blocked in blocked_domains):
                continue  # Skip this result

            results.append(url)
            if len(results) >= num_results:
                break

        return results
    else:
        print(f"Failed to fetch search results: {response.status_code}")
        return []


print(search_duckduckgo("tell me some good habits"))