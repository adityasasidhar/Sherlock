import re
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from readability import Document

def get_clean_article_text(url):
    print("get_clean_article_text function called")
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip() if article.text else "No text found."
    except Exception as e:
        print(f"Error extracting article: {e}")
        return "Failed to fetch article text."


def is_url(text):
    print("is_url function called")
    url_pattern = re.compile(
        r"^(https?|ftp)://[^\s/$.?#].\S*$", re.IGNORECASE
    )
    return bool(url_pattern.match(text))


with open('../apikey.txt', 'r') as f:
    print("Reading API key...")
    key = f.read()
    f.close()


def check_url(url):
    print("check_url function called")
    with open('../apikey.txt', 'r') as f:
        key = f.read()
        f.close()

    api_key = key
    suspicious_patterns = [
        r"[a-zA-Z0-9-]+\.(xyz|top|click|info|biz|gq|cf|tk|ml|ga|men|work|trade|loan)$",
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        r"(free|cheap|offer|win|bonus|prize|gift|reward|lottery|promo|hotdeal|discount|earnmoney|paynow|"
        r"fastcash|creditcard|bitcoin|forex|hack|unblock|download|crack|keygen|serial|giveaway|payperclick)\.",
    ]
    if any(re.search(pattern, url) for pattern in suspicious_patterns):
        return "unsafe (offline heuristic check)"

    # Step 2: Google Safe Browsing API check (More accurate but requires an API key)
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
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
    print("fetch_webpage function called")
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
    print("extract_text_from_html function called")
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
    print("getarticle_text function called")
    html = fetch_webpage(url)
    if html:
        return extract_text_from_html(html)
    return "Failed to fetch article text."


def search_duckduckgo(query, num_results=10):
    print("search_duckduckgo function called")
    query = query.replace(" ", "+")
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    blocked_domains = [
        # Shopping & E-commerce
        "amazon.", "flipkart.", "ebay.", "aliexpress.", "walmart.", "etsy.", "bestbuy.", "target.",
        "rakuten.", "newegg.", "shein.", "wayfair.", "overstock.", "zalando.", "mercari.", "poshmark.",
        "bigcommerce.", "shopify.", "groupon.", "kohls.", "macys.", "homedepot.", "lowes.", "costco.",
        "samsclub.", "chewy.", "asos.", "boohoo.", "prettylittlething.", "zappos.", "modcloth.", "lulus.",
        "urbanoutfitters.", "hollisterco.", "abercrombie.", "victoriassecret.", "nordstrom.", "sephora.",
        "ulta.", "bhphotovideo.", "adorama.", "microcenter.", "gamestop.", "nike.", "adidas.", "puma.",
        "reebok.", "underarmour.", "lulu.", "levi.", "timberland.", "clarks.", "crocs.", "drmartens.",
        "fossil.", "swatch.", "ray-ban.", "oakley.", "warbyparker.", "wayfair.", "pier1.", "ashleyfurniture.",
        "rooms-to-go.", "ikea.", "cb2.", "westelm.", "crateandbarrel.", "bedbathandbeyond.", "staples.",
        "officedepot.", "paperchase.", "michaels.", "hobbylobby.", "joann.", "partycity.", "shutterfly.",
        "vistaprint.", "snapfish.", "redbubble.", "society6.", "cafepress.", "teepublic.", "spreadshirt.",
        "zazzle.", "moonpig.", "funkypigeon.", "bluenile.", "jamesallen.", "kay.", "zales.", "tiffany.",
        "pandora.", "cartier.", "chanel.", "gucci.", "prada.", "louisvuitton.", "burberry.", "hermes.",
        "versace.", "dior.", "armani.", "ralphlauren.", "balenciaga.", "montblanc.", "swarovski.", "tagheuer.",

        # Social Media & Entertainment
        "facebook.", "twitter.", "instagram.", "linkedin.", "tiktok.", "reddit.", "pinterest.",
        "snapchat.", "tumblr.", "discord.", "threads.", "onlyfans.", "quora.", "weibo.", "wechat.",

        # Clickbait, Misinformation & Fake News
        "buzzfeed.", "dailystar.", "mirror.", "thethings.", "thelist.", "infowars.", "beforeitsnews.",
        "naturalnews.", "sputniknews.", "rt.", "newsmax.", "theblaze.", "yournewswire.", "zerohedge.",

        # AI-Generated & Scraper Sites
        "zergnet.", "boredpanda.", "viralnova.", "clickhole.", "diply.", "ranker.", "upworthy.",
        "patheos.", "yourtango.", "babylonbee.", "worldtruth.tv.",

        # Unsafe & Malware-Ridden Download Sites
        "softonic.", "cnet.com/downloads", "freedownloadmanager.", "getintopc.", "download.cnet.",
        "filehippo.", "softpedia.", "crackstreams.", "freetrialdownloads.", "warez-bb.", "filehorse.",
        "tucowsdownloads.", "oceanofgames.", "gameslopedy.", "igggames.",

        # Political Propaganda & Biased News
        "breitbart.", "thegatewaypundit.", "msnbc.", "huffpost.", "foxnews.", "oann.", "theintercept.",
        "dailywire.", "motherjones.", "rawstory.", "newstarget.",

        # Illegal & Unethical Content
        "thepiratebay.", "1337x.", "silkroadxx.", "crackserialkey.", "rarbg.", "yts.", "limetorrents.",
        "kickasstorrents.", "proxyrarbg.", "extratorrent.", "zippyshare.", "torrentz2.", "torrentdownloads.",
        "nzbplanet.", "warez-bb.", "ddlvalley.", "katcr.co.",

        # Gambling & Betting Sites
        "bet365.", "pokerstars.", "fanduel.", "draftkings.", "bovada.", "888casino.", "stake.", "unibet.",
        "williamhill.", "betfair.", "sportsbetting.", "ladbrokes.", "paddypower.", "dafabet.",

        # Adult Content
        "pornhub.", "xvideos.", "xnxx.", "redtube.", "youporn.", "brazzers.", "chaturbate.", "onlyfans.",
        "camsoda.", "erome.", "hclips.", "hentaihaven.", "f95zone.",

        # Cryptocurrency Scams & Ponzi Schemes
        "bitconnect.", "onecoin.", "usitech.", "gainbitcoin.", "hyperfund.", "forsage.", "cashfxgroup.",
        "mirrortradinginternational.", "trustinvesting.", "arbitraging.co.",

        # VPN & Proxy Services (If Blocking Circumvention)
        "hidemyass.", "protonvpn.", "nordvpn.", "expressvpn.", "surfshark.", "cyberghostvpn.", "privateinternetaccess.",
        "windscribe.", "tunnelbear.", "vpnunlimited.", "hotspotshield.", "freedom-vpn.",

        # Black Hat Hacking & Exploit Sites
        "hackforums.", "nulled.", "cracked.to.", "exploit-db.", "0day.today.", "raidforums.", "breachforums.",
        "dark0de.", "hackthissite.", "shadowforums.", "antichat.", "blackhatworld.", "crackingforum.",

        # Phishing & Scammer Domains
        "freegiftcards.", "winiphone.", "click4money.", "earnbitcoinfast.", "surveys-for-cash.", "claimprizes.",
        "lotterywinner.", "getrichquick.", "win-free-iphone.", "instantmillionaire.", "bitcoindoubler.",

        # Miscellaneous Unwanted Websites
        "fiverr.", "upwork.", "freelancer.", "99designs.", "peopleperhour.", "toptal.", "guru.", "taskrabbit.",
        "zeerk.", "workana.", "weworkremotely.", "truelancer.", "hubstafftalent.", "twago.", "flexjobs.",
    ]

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for result in soup.find_all("div", class_="result"):  # Each search result
            if "result--ad" in result.get("class", []) or "result__sponsored" in result.get("class", []):
                continue  # Skip sponsored results

            link_tag = result.find("a", class_="result__url")
            if link_tag:
                url = "https://" + link_tag.text.strip()

                # Block shopping & social media sites
                if any(blocked in url for blocked in blocked_domains):
                    continue  # Skip this result

                results.append(url)
                if len(results) >= num_results:
                    break

        return results
    else:
        print(f"Failed to fetch search results: {response.status_code}")
        return []