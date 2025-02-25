def add(text):
    with open('context.txt','w') as f:
        f.write(text)
        f.close()
        print("context added")

def get(text):
    with open('context.txt','r') as f:
        text = f.read()
        f.close()
        return text

def clear():
    with open('context.txt','w') as f:
        f.write("")
        f.close()
        print("context cleared")