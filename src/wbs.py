import re
import requests
from bs4 import BeautifulSoup
from newspaper import Article

def get_clean_article_text(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip() if article.text else "No text found."
    except Exception as e:
        print(f"Error extracting article: {e}")
        return "Failed to fetch article text."


def is_url(text):
    url_pattern = re.compile(
        r"^(https?|ftp)://[^\s/$.?#].\S*$", re.IGNORECASE
    )
    return bool(url_pattern.match(text))


with open('../apikey.txt', 'r') as f:
    key = f.read()


def check_url(url):
    print("Checking URL safety...")
    API_KEY = key
    suspicious_patterns = [
        r"[a-zA-Z0-9-]+\.(xyz|top|click|info|biz|gq|cf|tk|ml|ga|men|work|trade|loan)$",
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        r"(free|cheap|offer|win|bonus|prize|gift|reward|lottery|promo|hotdeal|discount|earnmoney|paynow|"
        r"fastcash|creditcard|bitcoin|forex|hack|unblock|download|crack|keygen|serial|giveaway|payperclick)\.",
    ]
    if any(re.search(pattern, url) for pattern in suspicious_patterns):
        return "unsafe (offline heuristic check)"

    # Step 2: Google Safe Browsing API check (More accurate but requires an API key)
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"
    data = {
        "client": {"clientId": "your_app", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    try:
        response = requests.post(api_url, json=data)
        if response.status_code == 200 and response.json() != {}:
            return "unsafe (Google Safe Browsing)"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "error"

    print("URL is safe")
    return "safe"

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
    for tag in soup(["script", "style", "iframe", "img", "video", "audio", "svg", "noscript", "aside", "footer"]):
        tag.decompose()

    # Try finding an article or main content div
    main_content = soup.find("article") or soup.find("main") or soup.find("div", class_="content")

    # Extract text from the best found content
    elements = main_content.find_all(["p", "h1", "h2", "h3", "li", "blockquote"]) if main_content else soup.find_all(["p", "h1", "h2", "h3", "li", "blockquote"])

    content = []
    for elem in elements:
        text = elem.get_text(strip=True)
        if text:
            if elem.name in ["h1", "h2", "h3"]:
                content.append(f"\n{text}\n")  # Keep headers structured
            elif elem.name == "li":
                content.append(f"• {text}")  # Format list items
            else:
                content.append(text)
    clean_text = "\n".join(content)
    return clean_text if clean_text else "No text content found."

def getarticle_text(url):
    html = fetch_webpage(url)
    if html:
        return extract_text_from_html(html)
    return "Failed to fetch article text."