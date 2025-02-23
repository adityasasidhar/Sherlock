from flask import Flask, request, jsonify, render_template
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import os
import re
import requests
from bs4 import BeautifulSoup
from newspaper import Article


def get_clean_article_text(url):
    html = fetch_webpage(url)
    if html:
        return extract_text_from_html(html)
    return "Failed to fetch article text."

def fetch_webpage(url, timeout=10):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException:
        return None

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "iframe", "img", "video", "audio", "svg", "noscript", "aside", "footer"]):
        tag.decompose()
    main_content = soup.find("article") or soup.find("main") or soup.find("div", class_="content")
    elements = main_content.find_all(["p", "h1", "h2", "h3", "li", "blockquote"]) if main_content else soup.find_all(["p", "h1", "h2", "h3", "li", "blockquote"])
    return "\n".join(elem.get_text(strip=True) for elem in elements) or "No text content found."

def is_url(text):
    return bool(re.match(r"^(https?|ftp)://[^\s/$.?#].\S*$", text, re.IGNORECASE))

API_KEY = os.getenv("", "").strip()

def check_url(url):
    suspicious_patterns = re.compile("|".join([
        r"[a-zA-Z0-9-]+\.(xyz|top|click|info|biz|gq|cf|tk|ml|ga|men|work|trade|loan)$",
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
        r"(free|cheap|offer|win|bonus|prize|gift|reward|lottery|promo|hotdeal|discount|earnmoney|paynow|"
        r"fastcash|creditcard|bitcoin|forex|hack|unblock|download|crack|keygen|serial|giveaway|payperclick)\."
    ]), re.IGNORECASE)
    if suspicious_patterns.search(url):
        return "unsafe (offline heuristic check)"
    if not API_KEY:
        return "error: API key missing"
    try:
        response = requests.post(
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}",
            json={
                "client": {"clientId": "your_app", "clientVersion": "1.0"},
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}],
                },
            }
        )
        if response.status_code == 200 and response.json():
            return "unsafe (Google Safe Browsing)"
    except requests.exceptions.RequestException:
        return "error"
    return "safe"

app = Flask(__name__)

model_name = "meta-llama/Llama-3.2-3B-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)
torch.cuda.empty_cache()
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=bnb_config, device_map=device)

def generate_response(query, context=""):
    context_tokens = tokenizer(context, return_tensors="pt", truncation=True, max_length=1500)
    query_tokens = tokenizer(query, return_tensors="pt", truncation=True, max_length=2300)
    inputs = {key: torch.cat([context_tokens[key], query_tokens[key]], dim=-1).to(device) for key in query_tokens}
    with torch.inference_mode():
        output = model.generate(**inputs, max_length=3800, num_return_sequences=1, do_sample=False, temperature=0.9, top_p=0.9)
    return tokenizer.batch_decode(output, skip_special_tokens=True)[0].replace(query, "").strip()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get("query", "")
    if query.lower() == "exit":
        open('context.txt', 'w').write(" ")
        return jsonify({"response": "Goodbye!"})
    context = ""
    if is_url(query) and check_url(query) == "safe":
        context = get_clean_article_text(query)[:2000]
        open('context.txt', 'w').write(context)
    return jsonify({"response": generate_response(query, context)})

if __name__ == "__main__":
    app.run(debug=True)
