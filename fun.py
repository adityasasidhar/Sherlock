import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

torch.cuda.empty_cache()

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
    device_map="auto",
    trust_remote_code=True
)
model.eval()

query = input("Enter query: ")

inputs = tokenizer(query, return_tensors="pt", padding=True)
inputs = {k: v.to(device) for k, v in inputs.items()}

with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=2400,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.8,
        top_p=0.9,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id
    )

response = tokenizer.batch_decode(output, skip_special_tokens=True)
print("\nResponse:\n", response[0])
