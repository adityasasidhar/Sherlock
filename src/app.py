import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from wbs import is_url, check_url, get_clean_article_text

def estimate_confidence(inputs):
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    last_token_logits = logits[0, -1, :]
    probabilities = torch.nn.functional.softmax(last_token_logits, dim=-1)

    max_prob = torch.max(probabilities).item()
    entropy = -torch.sum(probabilities * torch.log(probabilities)).item()
    return {"max_probability": max_prob, "entropy": entropy}

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
    device_map="cuda")

print("Model loaded successfully")
while True:
    query = input("You: ")
    if query.lower() == "exit":
        with open('../context.txt', 'w'):
            f.write(" ")
        print("Goodbye!")
        break
    if is_url(query) == True:
        if check_url(query) == "safe":
            print("URL is safe")
            context = get_clean_article_text(query)
            context = context[:1000]
            with open('../context.txt', 'w') as f:
                context = f.write(context)
                print("Context updated successfully")
            inputs = tokenizer(context,query, return_tensors="pt", padding=True, truncation=True, max_length=3500).to("cuda")
            print(estimate_confidence(inputs))
            output = model.generate(
                **inputs,
                max_length=3500,
                num_return_sequences=1,
                do_sample=False,
                temperature=0.7,
                top_p=0.9,
                eos_token_id=tokenizer.eos_token_id
            )
            response = tokenizer.batch_decode(output, skip_special_tokens=True)
            response = response[0]
            response = response.replace(query, "").strip()
            response = response.replace(context,"").strip()
            tokens = tokenizer(response, return_tensors="pt").input_ids.shape[1]
            print(f"Number of tokens in response: {tokens}")
            print(f"Assistant: {response}")
        else:
            continue

    else:
        inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True, max_length=3800).to("cuda")
        print(estimate_confidence(inputs))
        output = model.generate(
            **inputs,
            max_length=3800,
            num_return_sequences=1,
            do_sample=False,
            temperature=0.9,
            top_p=0.9,
            eos_token_id=tokenizer.eos_token_id
        )
        response = tokenizer.batch_decode(output, skip_special_tokens=True)
        response = response[0]
        response = response[len(query):].strip()
        response = response.replace(query, "").strip()
        tokens = tokenizer(response, return_tensors="pt").input_ids.shape[1]
        print(f"Number of tokens in response: {tokens}")
        print(f"Assistant: {response}")

