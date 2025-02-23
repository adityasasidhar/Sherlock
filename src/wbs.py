import re
import requests
from bs4 import BeautifulSoup

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
    for tag in soup(["script", "style", "iframe", "img", "video", "audio", "svg"]):
        tag.decompose()
    article = soup.find("article")
    if article:
        paragraphs = article.find_all("p")
        headers = article.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        lists = article.find_all(["ul", "li"])
    else:
        # Fallback: Extract text from the entire page
        paragraphs = soup.find_all("p")
        headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        lists = soup.find_all(["ul", "li"])
    content = []

    for header in headers:
        content.append(f"\n{header.get_text(strip=True)}\n")  # Keep heading structure

    for para in paragraphs:
        text = para.get_text(strip=True)
        if text:
            content.append(text)

    for lst in lists:
        for li in lst.find_all("li"):
            content.append(f"• {li.get_text(strip=True)}")  # Format list items

    clean_text = "\n".join(content)
    return clean_text if clean_text else "No text content found."

def get_clean_article_text(url):
    html = fetch_webpage(url)
    if html:
        return extract_text_from_html(html)
    return "Failed to fetch article text."