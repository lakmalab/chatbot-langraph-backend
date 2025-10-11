from langchain_core.tools import tool
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import text
from typing import Dict, Any

_db_session: DBSession = None
from app.db.connection import get_db

def set_db_session(db: DBSession):
    global _db_session
    _db_session = db


@tool
def execute_dynamic_sql_query(sql_query: str) -> Dict[str, Any]:
    """
        Execute a dynamic SQL query against the database and return the results.
        """
    try:
        db_gen = get_db()
        db_session = next(db_gen)
        result = db_session.execute(text(sql_query))

        rows = result.fetchall()

        if not rows:
            try:
                next(db_gen)
            except StopIteration:
                pass
            return {
                "success": True,
                "message": "Query executed successfully but returned no results",
                "row_count": 0,
                "data": [],
                "query_executed": sql_query
            }

        columns = result.keys()
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                if hasattr(value, '__float__'):
                    value = float(value)
                row_dict[col] = value
            data.append(row_dict)

        return {
            "success": True,
            "row_count": len(data),
            "columns": list(columns),
            "data": data,
            "query_executed": sql_query
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"SQL execution error: {str(e)}",
            "query_attempted": sql_query
        }
