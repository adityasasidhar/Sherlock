import torch
import logging
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from src.wbs import search_duckduckgo
from wbs import is_url, check_url, get_clean_article_text
from file import add, get, clear
from gpu import clear_cuda_memory, check_cuda_memory

logging.basicConfig(level=logging.DEBUG)
check_cuda_memory()

context = ""

"""
1) The first thing that this code does is load the model and tokenizer from the Hugging Face model hub.

2) It then defines a function called fetch_webpage that fetches the HTML content of a webpage given a URL and defines

   new function called extract_text_from_html that extracts the text content from the HTML.
   
3) The get_clean_article_text function combines the two functions above to fetch and extract the text content from a webpage.

4) Then it writes it onto the context file

5) The code then reads the context from a file called content.txt

"""
model_name = "meta-llama/Llama-3.2-3B-Instruct"

device = "cuda" if torch.cuda.is_available() else "cpu"
torch.backends.cuda.matmul.allow_tf32 = True

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
    device_map="cuda"
)
print("model loaded")
check_cuda_memory()

def estimate_confidence(question):
    inputs = tokenizer(question, return_tensors="pt", padding=True, truncation=True).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    last_token_logits = logits[0, -1, :]
    probabilities = torch.nn.functional.softmax(last_token_logits, dim=-1)
    max_prob = torch.max(probabilities).item()
    entropy_value = -torch.sum(probabilities * torch.log(probabilities)).item()
    print(f"Max probability: {max_prob}")
    print(f"Entropy: {entropy_value}")
    return {"max_probability": max_prob, "entropy": entropy_value}

while True:
    query = input("You: ")
    if query.lower() == "exit":
        break
    if is_url(query):
        if check_url(query) == "safe":
            context = get_clean_article_text(query)
            context = context[:3500]
            logging.info("Context: %s", context)
            inputs = tokenizer(context, query, return_tensors="pt",
                               padding=True, truncation=True,
                               max_length=3300)
            inputs = {key: value.to(device) for key, value in inputs.items()}
            print(estimate_confidence(inputs))
            output = model.generate(
                **inputs,
                max_new_tokens=3300,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.eos_token_id
            )
            response = tokenizer.batch_decode(output, skip_special_tokens=True)
            response = response[0]
            response = response[len(query):].strip()
            response = response.replace(query, "").strip()
            tokens = tokenizer(response, return_tensors="pt").input_ids.shape[1]
            print(f"Number of tokens in response: {tokens}")
            print(f"Assistant: {response}")
            context += response
            context = context[-3500:]
        else:
            continue

    else:
        logging.info("Context: %s", context)
        confidence_data = estimate_confidence(query)
        confidence = confidence_data["max_probability"]
        if confidence > 0.2:
            inputs = tokenizer(context, query, return_tensors="pt",
                               padding=True, truncation=True,
                               max_length=3300)
            inputs = {key: value.to(device) for key, value in inputs.items()}
            output = model.generate(
                **inputs,
                max_new_tokens=3300,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.9,
                top_p=0.9,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.eos_token_id
            )
            response = tokenizer.batch_decode(output, skip_special_tokens=True)
            response = response[0]
            response = response[len(query):].strip()
            response = response.replace(query, "").strip()
            tokens = tokenizer(response, return_tensors="pt").input_ids.shape[1]
            print(f"Number of tokens in response: {tokens}")
            print(f"Assistant: {response}")
            context += response
            context = context[-3500:]

        else:
            search_results = search_duckduckgo(query)
            url = search_results[0]
            print(f"URL: {url}")
            if check_url(url) == "safe":
                context = get_clean_article_text(url)
                context = context[:2000]
                logging.info("Context: %s", context)
                inputs = tokenizer(context, query, return_tensors="pt",
                                   padding=True, truncation=True,
                                   max_length=3300)
                inputs = {key: value.to(device) for key, value in inputs.items()}
                output = model.generate(
                    **inputs,
                    max_new_tokens=3300,
                    num_return_sequences=1,
                    do_sample=True,
                    temperature=0.9,
                    top_p=0.9,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.eos_token_id
                )
                response = tokenizer.batch_decode(output, skip_special_tokens=True)
                response = response[0]
                response = response[len(query):].strip()
                response = response.replace(query, "").strip()
                tokens = tokenizer(response, return_tensors="pt").input_ids.shape[1]
                print(f"Number of tokens in response: {tokens}")
                print(f"Assistant: {response}")
                context += response
                context = context[-3500:]
            else:
                continue