from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.core.config import settings
from app.enums import AiModel


def classify_intent(state: AgentState) -> AgentState:
    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    system_prompt = """
                    You are an intent classifier for a Pension Scheme Chatbot. 
                    Your job is to classify the user's latest message into ONE of the following intent categories:
                
                    1. **calculate**  
                       - The user wants to calculate or retrieve any *pension-related value*, *premium amount*, *future pension amount*, or *other numeric details* from the pension database.  
                       - This includes any mention of **age, pension amount, payment method, duration, interest, policy term, or contribution frequency**.  
                       - If the message implies a computation or lookup of data (even indirectly), choose this.  
                       - Examples:
                         - "I'm 30 and want 5000 pension"
                         - "How much should I pay monthly for 10k pension?"
                         - "What pension do I get at 60?"
                         - "Calculate my premium"
                         - "Show me pension table for age 35"
                         - "Get details from pension database"
                
                    2. **question**  
                       - The user is asking about *general information*, *rules*, *benefits*, *eligibility*, or *policy features* of the pension scheme — not requesting an actual numeric calculation.  
                       - Examples:
                         - "What is the eligibility?"
                         - "How does the scheme work?"
                         - "Is it government-backed?"
                         - "Can I withdraw early?"
                
                    3. **greeting**  
                       - The user is just greeting, starting, or ending the conversation.  
                       - Examples:
                         - "Hi", "Hello", "Good morning", "Thanks", "Bye"
                
                    4. **unclear**  
                       - The message is unrelated to pensions or completely off-topic.  
                       - Examples:
                         - "Tell me a joke"
                         - "Who won the football match?"
                         - "What's the weather like?"
                         - "Order me a pizza"
                
                    **Classification Rules:**
                    - Always prioritize "calculate" if the message involves **numbers**, **pension**, or **premium calculations**, even if phrased as a question.  
                    - If the message has *nothing to do with the pension scheme*, classify it as "unclear".  
                    - Respond with **only one word**: `calculate`, `question`, `greeting`, or `unclear`.
                    """

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)
    intent = response.content.strip().lower()

    valid_intents = ["calculate", "question", "greeting", "unclear"]

    if intent not in valid_intents:
        intent = "unclear"

    state["intent"] = intent
    print(f"Classified intent: {intent}")
    return state
