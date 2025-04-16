import os

import indexing
from langchain_community.document_loaders import WebBaseLoader, UnstructuredPDFLoader
import re

# indexing.indexing(input_path=r"E:\Data\File\661_03242025114448888.pdf")
# print(load_document(r"C:\Users\asus\Downloads\spring-boot-up-and-running-building-cloud-native-java-and-kotlin-applications-1.pdf"))

"""
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import time
query = "Kế hoạch phát bằng tốt nghiệp"

# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb\eb")


from mxbai_rerank import MxbaiRerankV2
rerank_model = MxbaiRerankV2("mixedbread-ai/mxbai-rerank-base-v2")

# docs = vector_store.get()
# print(docs)
"""

if __name__ == "__main__":
    # docs = indexing.load_file(file_path=r"E:\Data\File\661_03242025114448888.pdf", language="vie")
    # docs = indexing.load_file(file_path=r"E:\Data\File\BERT.pdf")
    docs = indexing.load_audio_video(link="https://www.youtube.com/watch?v=gZSxDDqVZO0&ab_channel=DWNews")
    print(docs)