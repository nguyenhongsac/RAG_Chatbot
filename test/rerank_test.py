from dotenv import load_dotenv
import os
import time
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb")

query = "Hiệu trưởng là ai?"
docs = vector_store.similarity_search(query=query, k=30)

from components.rerank_model import RerankModel
t1 = time.time()
rerank_model = RerankModel()
texts = [d.page_content for d in docs]
doc_map = {doc.page_content: doc for doc in docs}
# get top_k 
res = rerank_model.rank(query=query, documents=texts, top_k=5)
retrieved_docs = []
for text in res:
    if text in doc_map:
        retrieved_docs.append(doc_map[text])
t2 = time.time()
print(retrieved_docs)
print(f"Time: {t2-t1}s")