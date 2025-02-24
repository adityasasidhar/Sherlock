from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

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