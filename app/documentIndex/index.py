from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os

from app.core.config import settings

os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY

SOURCE_FILE = Path("Farmers.pdf")
INDEX_DIR   = Path("chroma_db_1")
EMBED_MODEL = "text-embedding-3-small"

if not SOURCE_FILE.exists():
    raise FileNotFoundError(f"PDF not found at {SOURCE_FILE.resolve()}")
if SOURCE_FILE.suffix == ".pdf":
    docs = PyPDFLoader(str(SOURCE_FILE)).load()
elif SOURCE_FILE.suffix == ".docx":
    docs = Docx2txtLoader(str(SOURCE_FILE)).load()
else:
    raise ValueError("Unsupported file type  only .pdf or .docx accepted")


splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)


embeddings = OpenAIEmbeddings(model=EMBED_MODEL)


vectordb = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=str(INDEX_DIR),
    collection_name="kb_collection",
)
vectordb.persist()

print("✅ Index built →", INDEX_DIR.resolve())
