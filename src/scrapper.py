import requests
from bs4 import BeautifulSoup

def fetch_webpage(url, timeout=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Try extracting from <article> tags first
    article = soup.find("article")
    if article:
        paragraphs = article.find_all("p")
    else:
        # Fallback: Extract all <p> tags
        paragraphs = soup.find_all("p")

    # Extract and clean text
    article_text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    # If no article content is found, return full webpage text as a last resort
    if not article_text:
        article_text = soup.get_text( separator="\n", strip=True)

    return article_text if article_text else "No article content found."

def get_clean_article_text(url):
    html = fetch_webpage(url)
    if html:
        return extract_text_from_html(html)
    return "Failed to fetch article text."
