import torch
import requests
from bs4 import BeautifulSoup
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

"""
1) The first thing that this code does is load the model and tokenizer from the Hugging Face model hub.

2) It then defines a function called fetch_webpage that fetches the HTML content of a webpage given a URL and defines

   new function called extract_text_from_html that extracts the text content from the HTML.
   
3) The get_clean_article_text function combines the two functions above to fetch and extract the text content from a webpage.

4) Then it writes it onto the conetxt file

5) The code then reads the context from a file called history.txt

"""
torch.backends.cuda.matmul.allow_tf32 = True
model_name = "meta-llama/Llama-3.2-3B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4",
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="cuda",
    use_cache = True
)

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

with open('../history.txt', 'r') as f:
    contxt = f.read()

def estimate_confidence(inputs):
    with torch.inference_mode():
        outputs = model(**inputs)
    logits = outputs.logits
    last_token_logits = logits[0, -1, :]
    probabilities = torch.nn.functional.softmax(last_token_logits, dim=-1)

    max_prob = torch.max(probabilities).item()
    entropy = -torch.sum(probabilities * torch.log(probabilities)).item()
    return {"max_probability": max_prob, "entropy": entropy}

print("Model loaded successfully")
query = input("prompt: ")

inputs = tokenizer(contxt,query, return_tensors="pt", padding=True, truncation=True,max_length=2200).to("cuda")
print(estimate_confidence(inputs))
output = model.generate(
    **inputs,
    max_length = 3000,
    num_return_sequences=1,
    do_sample=False,
    temperature=0.8,
    top_p=0.9,
    eos_token_id=tokenizer.eos_token_id
)
response = tokenizer.batch_decode(output, skip_special_tokens=True)
response = response[0]
response = response[len(query):].strip()


tokens = tokenizer(response, return_tensors="pt").input_ids.shape[1]
print(f"Number of tokens in response: {tokens}")
print(response)
torch.cuda.empty_cache()
f.close()