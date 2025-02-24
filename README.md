# 🕵️‍♂️ Sherlock - Your Private AI Detective 🔍

Sherlock is a **cross-platform, privacy-focused AI assistant** that scouts the internet for you, analyzes URLs, extracts webpage content, and provides insightful answers—all while ensuring **your data stays on your device**. 🚀🔒 No external data collection, no cloud dependency—just **pure intelligence, right on your machine!** 💻

---

## ✨ Features

- 🛡️ **Privacy-First**: Sherlock runs locally on your device with **zero data leaks**.
- 🌎 **Multi-Platform Support**: Works seamlessly on **Windows, macOS, and Linux**.
- 🔍 **Smart Information Retrieval**: Searches the web **in real-time** to get accurate and up-to-date results.
- 🕵️‍♂️ **Advanced URL Investigation**: Analyzes websites for **safety** and extracts their content for deeper insights.
- 🤖 **AI-Powered Contextual Answers**: Uses retrieved data to answer queries with high precision.
- ⚡ **Optimized Performance**: Supports **GPU acceleration** via CUDA (if available) for blazing-fast responses.
- 📡 **Offline Mode**: Stores and processes previously fetched content **without internet access**.

---

## 📌 Requirements

- ✅ **Python 3.8 or later**
- ✅ **Windows, macOS, or Linux**
- ✅ **A CUDA-enabled GPU (optional for speed boost 🚀)**
- ✅ **Dependencies from `requirements.txt`**

---

## 🔧 Installation

1️⃣ **Clone the Repository**:
```bash
git clone https://github.com/adityasasidhar/sherlock.git
cd sherlock
```

2️⃣ **Create and Activate a Virtual Environment**:
   - **Windows:**
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3️⃣ **Install Dependencies**:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

- 🔑 **Set your Google Safe Browsing API key** in `config.json`.
- 🏗️ **Ensure the model (e.g., `meta-llama/Llama-3.2-3B-Instruct`) is available.**
- 🎛️ **Customize settings** such as verbosity and offline mode in `config.json`.

---

## 🚀 Usage

### 🏁 Run Sherlock
```bash
python src/app.py
```

### 🌐 Investigate a URL
```bash
python src/app.py --url "https://example.com"
```

### 🔎 Search for Information
```bash
python src/app.py --query "Latest AI advancements"
```

### 📊 Check GPU Memory Usage (Optional)
```bash
python utils/cuda_memory_check.py
```

---

## 📂 Code Structure

- 📜 **`src/app.py`** → Main AI logic (queries, URL analysis, text generation)
- 📋 **`requirements.txt`** → All required Python dependencies
- ⚙️ **`config.json`** → API keys & settings
- 🖥️ **`utils/cuda_memory_check.py`** → GPU memory checker

---

🚀 **Sherlock - Your AI-powered digital detective, right on your PC!** 🕵️‍♂️🔍 Stay secure, stay informed, and let Sherlock do the scouting for you. 🌎💡

💙 Made with privacy in mind. No tracking. No data leaks. Just pure intelligence. 💡🔒

