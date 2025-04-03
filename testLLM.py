import os
import getpass
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb")


# LLM
if not os.environ.get("GROQ_API_KEY"):
  os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")
from langchain.chat_models import init_chat_model
llm = init_chat_model("llama3-8b-8192", model_provider="groq")

from mxbai_rerank import MxbaiRerankV2
rerank_model = MxbaiRerankV2("mixedbread-ai/mxbai-rerank-base-v2")

query = "Hiệu trưởng là ai?"
docs = vector_store.similarity_search(query=query, k=35)

# Create a dictionary to map text to full document objects
doc_map = {doc.page_content: doc for doc in docs}

# Extract just the text for reranking
documents = [doc.page_content for doc in docs]

# Perform reranking
ranked_documents = rerank_model.rank(
    query=query,
    documents=documents,  # Only pass the text for ranking
    return_documents=True,
    top_k=5
)

context = []
for text in ranked_documents:
  if text.document in doc_map:
    context.append(doc_map[text.document])

print(context)