from app.documentIndex.index import vectordb
from langchain_core.tools import tool

retriever = vectordb.as_retriever(search_kwargs={"k": 2})


@tool
def rag_search_tool(query: str) -> str:
    """Search the knowledge-base for relevant chunks answer in a conversational way."""
    results = retriever.invoke(query)
    return "".join(d.page_content for d in results)
