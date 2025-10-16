from app.agents.state import AgentState
from app.agents.tools.execute_dynamic_sql_query import execute_dynamic_sql_query

def execute_sql_tool_node(state: AgentState) -> AgentState:

    sql = state.get("generated_sql")
    if not sql:
        state["response"] = "No SQL query was generated."
        state["tool_results"] = ""
        return state

    result = execute_dynamic_sql_query.invoke({"sql_query": sql})
    state["tool_results"] = result

    if result["success"]:
        data = result.get("data", [])
        if not data:
            state["response"] = "Query ran successfully but returned no results."
        elif len(data) == 1:
            row = data[0]
            state["response"] = "Result:\n" + "\n".join(f"- {k}: {v}" for k, v in row.items())
        else:
            text = f"Found {len(data)} results (showing first 5):\n"
            for i, row in enumerate(data[:5], 1):
                text += f"\nResult {i}:\n" + "\n".join(f"  - {k}: {v}" for k, v in row.items())
            if len(data) > 5:
                text += f"\n...and {len(data) - 5} more results"
            state["response"] = text
    else:
        state["response"] = f"Error executing query: {result['error']}"

    print(f"SQL Execution Results: {result}")
    return state
