# Langraph Agentic AI Chat Assistant

An intelligent **Agentic AI Chat Assistant** powered by LangGraph — designed to classify user intent, extract key data, and perform dynamic calculations such as pension or insurance estimation.

---

## 🧠 How It Works

**Example:**

```
User: "I am 30 and want 50k pension"
           ↓
    [LangGraph Graph]
           ↓
┌─────────────────────┐
│ Node 1: Classify    │ → "pension / crop insurance / vehicle insurance"
│ Intent              │
└──────────┬──────────┘
           │
           │  "pension" intent detected
           │
           ↓
┌─────────────────────┐
│ Node 2: Extract     │ → age = 30, pension = 50000
│ Parameters          │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Node 3: Calculate   │ → Uses PensionCalculator
│ Pension             │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Node 4: Generate    │ → Natural language response
│ Response            │
└─────────────────────┘
```

---

## ⚙️ Setup Instructions

*(Written painlessly for you by Lakmalllllll 😎)*

### 🧩 Prerequisites

> **⚠️ Requires Python 3.10 or higher**

---

### 🏗️ Create a virtual environment

```bash
python -m venv .venv
```

### ▶️ Activate the environment

**Windows (Command Prompt):**

```bash
.venv\Scripts\activate
```

**Windows (PowerShell):**

```bash
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

---

### 🔑 Environment Variables

> I accidentally committed the `.env` file (good for you! 😅)
> Just open it and add the following:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_AI_MODEL=your_openai_mdel_name
```

---

### 📦 Install dependencies

Using **pip**:

```bash
pip install -r requirements.txt
```

Or if you’re a **UV** fan like me:

```bash
uv pip install -r requirements.txt
```

---

### 🚀 Run the application

```bash
uvicorn main:app --reload
```

Your app will start at:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

API Docs are available at:
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

💡 **Tip:** You can now talk to your AI agent about pensions, vehicles, or crop insurance, and watch the LangGraph nodes do their magic.
