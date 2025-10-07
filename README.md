Langraph Agentic AI Chat Assisitant
#-----------------------------------#

# Setup Instructions written painlessly for you by me Lakmalllllll
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