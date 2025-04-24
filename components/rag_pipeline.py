import logging
from typing import List, AsyncGenerator
from langchain_core.documents import Document
from langchain_together import ChatTogether
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from mxbai_rerank import MxbaiRerankV2
from langchain.prompts import PromptTemplate
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_MODEL: str = "deepseek-ai/DeepSeek-V3"
    EMBEDDINGS_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    CHROMA_PERSIST_DIR: str = r"E:\Data\chromadb"
    RERANK_MODEL: str = "mixedbread-ai/mxbai-rerank-base-v2"

    class Config:
        env_file = ".env"

settings = Settings()

logger = logging.getLogger(__name__)


llm = ChatTogether(
    model=settings.LLM_MODEL,
    temperature=0,
    max_tokens=None,
    timeout=None
)

embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDINGS_MODEL)

vector_store = Chroma(embedding_function=embeddings, persist_directory=settings.CHROMA_PERSIST_DIR)

rerank_model = MxbaiRerankV2(settings.RERANK_MODEL)

# Define a Vietnamese prompt
prompt_template = """Bạn là một chatbot hỏi đáp thông minh. Hãy cung cấp câu trả lời chính xác dựa trên dữ liệu liên quan. Nếu bạn không biết câu trả lời, chỉ cần nói không biết. 
Phản hồi bằng tiếng Việt một cách tự nhiên, trình bày khoa học. Không lặp lại câu hỏi của người dùng.

Câu hỏi: {question}

Dữ liệu liên quan:
{context}
"""
prompt = PromptTemplate.from_template(prompt_template)


class RAGService:
    def __init__(self):
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 30})

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
        docs = self.retriever.invoke(question)
        top_docs = self._rerank_docs(question, docs)
        context = "\n\n".join(d.page_content for d in top_docs)
        messages = prompt.invoke({"question": question, "context": context})

        response = llm.invoke(messages)
        return {
            "answer": response.content,
            "sources": [d.metadata for d in top_docs]
        }

    async def ask_stream(self, question: str) -> AsyncGenerator[str, None]:
        docs = self.retriever.invoke(question)
        top_docs = self._rerank_docs(question, docs)
        context = "\n\n".join(d.page_content for d in top_docs)
        prompt = prompt.invoke({"question": question, "context": context})

        # Stream‐in tokens
        async for token in llm.stream(prompt):
            # SSE formatting
            yield f"data: {token}\n\n"