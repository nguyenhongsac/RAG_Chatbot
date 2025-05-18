import logging
from typing import List, AsyncGenerator
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from mxbai_rerank import MxbaiRerankV2
from pydantic_settings import BaseSettings
from components.llm_model import DeepSeekLLM

import time

class Settings(BaseSettings):
    EMBEDDINGS_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    RERANK_MODEL: str = "mixedbread-ai/mxbai-rerank-base-v2"
    CHROMA_PERSIST_DIR: str = r"E:\Data\chromadb"
    DEEPSEEK_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


llm = DeepSeekLLM(api_key=settings.DEEPSEEK_API_KEY)

embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDINGS_MODEL)

vector_store = Chroma(embedding_function=embeddings, persist_directory=settings.CHROMA_PERSIST_DIR)

rerank_model = MxbaiRerankV2(settings.RERANK_MODEL)

class RAGService:
    def __init__(self):
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    def _rerank_docs(self, question: str, docs: List[Document]) -> List[Document]:
        texts = [d.page_content for d in docs]
        doc_map = {doc.page_content: doc for doc in docs}
        # get top_k 
        res = rerank_model.rank(query=question, documents=texts, top_k=5, return_documents=True)
        retrieved_docs = []
        for text in res:
            if text.document in doc_map:
                retrieved_docs.append(doc_map[text.document])
        return retrieved_docs

    async def ask(self, question: str) -> dict:
        t1 = time.time()
        docs = self.retriever.invoke(question)
        t2 = time.time()
        logger.info(f"[RETRIEVE] Vector search: {t2 - t1}s")

        top_docs = self._rerank_docs(question, docs)
        t3 = time.time()
        logger.info(f"[RETRIEVE] Rerank: {t3 - t2}s")

        context = "\n\n".join(d.page_content for d in top_docs)
        messages = f"Câu hỏi: {question}. Dữ liệu liên quan:{context}"

        response = llm.invoke(messages)
        t4 = time.time()
        logger.info(f"[LLM] Response: {t4 - t3}s, TOTAL: {t4 - t1}")
        return {
            "answer": response.content,
            "sources": [d.metadata for d in top_docs]
        }

    async def ask_stream(self, question: str) -> AsyncGenerator[str, None]:
        docs = self.retriever.invoke(question)
        # top_docs = self._rerank_docs(question, docs)
        context = "\n\n".join(d.page_content for d in docs)
        prompt = f"Câu hỏi: {question}. Dữ liệu liên quan:{context}"

        # Stream‐in tokens
        async for token in llm.ainvoke(prompt):
            # SSE formatting
            yield f"data: {token}\n\n"