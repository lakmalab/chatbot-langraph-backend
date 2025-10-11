from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from app.agents.llm_provider import get_llm
from app.agents.state import AgentState
from app.agents.tools.execute_dynamic_sql_query import execute_dynamic_sql_query
from app.enums import AiModel


def execute_sql_tool_node(state: AgentState) -> AgentState:

    llm = get_llm(temperature=0, provider=AiModel.OPENAI)

    generated_sql = state.get("generated_sql")

    if not generated_sql:
        state["response"] = "No SQL query was generated. Please try again."
        state["tool_results"] = None
        return state

    tool_result = execute_dynamic_sql_query.invoke({
        "sql_query": generated_sql
    })

    state["tool_results"] = tool_result

    if tool_result["success"]:
        if "data" in tool_result and tool_result["data"]:
            data = tool_result["data"]
            if len(data) == 1:
                result_text = "Here are the results:\n"
                for key, value in data[0].items():
                    result_text += f"- {key}: {value}\n"
            else:
                result_text = f"Found {len(data)} results:\n"
                for i, row in enumerate(data[:5], 1):
                    result_text += f"\nResult {i}:\n"
                    for key, value in row.items():
                        result_text += f"  - {key}: {value}\n"

                if len(data) > 5:
                    result_text += f"\n... and {len(data) - 5} more results"
        else:
            result_text = "Query executed successfully."
    else:
        result_text = f"Error executing query: {tool_result['error']}"

    state["response"] = result_text
    print(f"SQL Execution Results: {tool_result}")

    return state