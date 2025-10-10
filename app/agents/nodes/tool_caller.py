# app/agents/nodes/tool_caller.py
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.core.config import settings
import json

from app.enums import AiModel


def call_tools(state: AgentState, tools: list) -> AgentState:

    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    llm_with_tools = llm.bind_tools(tools)

    conversation_context = "\n".join([msg.content for msg in state["messages"][-5:]])

    context_info = f"User's current query: {state['user_query']}\n"
    context_info += f"Intent: {state.get('intent')}\n"

    if state.get("current_age"):
        context_info += f"User's age: {state['current_age']}\n"
    if state.get("desired_pension"):
        context_info += f"Desired pension: Rs. {state['desired_pension']}\n"
    if state.get("monthly_premium"):
        context_info += f"Asking about premium: Rs. {state['monthly_premium']}\n"

    system_prompt = """You are a pension scheme assistant with access to these tools:

                        1. **get_available_plans**: Get all available pension plans with premiums and payouts
                           - Use when: User asks "what plans?" or "show me options"
                        
                        2. **calculate_premium_by_age**: Calculate required premium based on age and desired pension
                           - Use when: User provides age and desired pension amount
                           - Args: current_age (18-55), desired_pension (amount)
                        
                        3. **get_pension_for_premium**: Get pension amounts for a specific premium
                           - Use when: User asks "what pension for Rs. X?"
                           - Args: monthly_premium (27, 270, or 2700)
                        
                        4. **compare_plans_for_age**: Compare all plans for a specific age
                           - Use when: User asks to compare or see options for their age
                           - Args: current_age (18-55)
                        
                        Choose the appropriate tool(s) based on the user's intent and available parameters.
                        You can call multiple tools if needed."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"{context_info}\nConversation:\n{conversation_context}")
    ]


    response = llm_with_tools.invoke(messages)

    tool_results = []
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_func = next((t for t in tools if t.name == tool_call["name"]), None)
            if tool_func:
                try:
                    print(f"Calling tool: {tool_call['name']} with args: {tool_call['args']}")

                    result = tool_func.invoke(tool_call["args"])
                    tool_results.append({
                        "tool": tool_call["name"],
                        "result": result
                    })

                    if tool_call["name"] == "calculate_premium_by_age" and isinstance(result,
                                                                                      dict) and "error" not in result:
                        state["calculation_result"] = result
                        state["current_age"] = result.get("current_age")
                        state["desired_pension"] = result.get("pension_breakdown", {}).get("60-63")

                except Exception as e:
                    print(f" Tool error: {e}")
                    tool_results.append({
                        "tool": tool_call["name"],
                        "error": str(e)
                    })

    state["tool_results"] = tool_results

    return state