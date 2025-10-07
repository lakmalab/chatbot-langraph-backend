# Langraph Agentic AI Chat Assisitant
#-----------------------------------#

User: "I am 30 and want 50k pension"
           ↓
    [LangGraph Graph]
           ↓
┌─────────────────────┐
│ Node 1: Classify    │ → "pension / crop insurance / Vehicle insurance"
│ Intent              │
└──────────┬──────────┘
           |         "pension" intent detected
           |         since user wants to 
           ↓         calculate pension
┌─────────────────────┐
│ Node 2: Extract     │ → age=30, pension=50000
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

---Setup Instructions written painlessly for you by me Lakmalllllll---

steps to set up the development environment:
#############Warning - NEED Python 3.10 or Higher###########################

create virtual environment:
  python -m venv .venv

activate virtual environment:
    # For Windows (Command Prompt)
    .\.venv\Scripts\activate
    # For Windows (PowerShell)
    .\venv\Scripts\Activate.ps1
    # For macOS/Linux
    source .venv/bin/activate

I mistakenly committed the .env file (good for you!!!) just add your OPENAI_API_KEY and OPENAI_AI_MODEL in .env file

install dependencies:
      pip install -r requirements.txt
    or if you prefer UV like me 
      uv pip install -r requirements.txt

run the application:
    uvicorn main:app --reload   