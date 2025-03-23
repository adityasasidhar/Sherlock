import requests

context = ""

web_context = ""

with open('groq.txt', 'r') as f:
    api_key = f.read()
    f.close()

# Groq API endpoint and headers
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

system_prompt = {
    "role": "system",
    "content": (
        "You are an expert AI assistant that helps people browse. "
        "If a person asks a query, ill give you the context with some articles online and use the information if you deem it necessary and give short and concise summaries "
        "Respond in a clear and helpful manner."

    )
}

chat_history = [system_prompt]

def get_bot_response(user_input):
    chat_history.append({"role": "user", "content": user_input})

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": chat_history,
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        bot_reply = response.json()["choices"][0]["message"]["content"].strip()
        chat_history.append({"role": "assistant", "content": bot_reply})
        return bot_reply
    else:
        return f"Error: {response.status_code}, {response.text}"

if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        response = get_bot_response(user_input)
        print(f"Chatbot: {response}\n")
        context += response


