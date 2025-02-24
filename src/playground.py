import requests
from bs4 import BeautifulSoup


def search_duckduckgo(query, num_results=10):
    query = query.replace(" ", "+")
    url = f"https://html.duckduckgo.com/html/?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # Extract search result links
        for link in soup.find_all("a", class_="result__url"):
            results.append("https://" + link.text.strip())

            if len(results) >= num_results:
                break

        return results
    else:
        print(f"Failed to fetch search results: {response.status_code}")
        return []

#return a list of URLs from the search results
