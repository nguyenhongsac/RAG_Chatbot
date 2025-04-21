import os
from dotenv import load_dotenv
from langchain_together import ChatTogether
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from mxbai_rerank import MxbaiRerankV2

load_dotenv()

llm = ChatTogether(
    model="deepseek-ai/DeepSeek-V3",
    temperature=0,
    max_tokens=None
)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

persist_path = os.getenv("CHROMA_PERSIST_DIR")
vector_store = Chroma(embedding_function=embeddings, persist_directory=persist_path)

rerank_model = MxbaiRerankV2("mixedbread-ai/mxbai-rerank-base-v2")