import os
import components.indexing_pipeline as indexing_pipeline
from langchain_community.document_loaders import WebBaseLoader, UnstructuredPDFLoader
import re
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import time

# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb")


# from mxbai_rerank import MxbaiRerankV2
# rerank_model = MxbaiRerankV2("mixedbread-ai/mxbai-rerank-base-v2")

# docs = vector_store.get()
# print(docs)


from langchain_community.document_loaders import BSHTMLLoader

if __name__ == "__main__":

    path = r"E:\Data\File\pdf"
    # for f in os.listdir(path=path):
    #     file_path = path + '/' + f
    #     indexing.indexing(input_path=file_path, language="vie")

    # weblink = ["https://sict.haui.edu.vn/vn/html/thong-tin-chung", "https://sict.haui.edu.vn/vn/html/bo-may-to-chuc",
    #            "https://sict.haui.edu.vn/vn/html/chien-luoc-phat-trien", "https://sict.haui.edu.vn/vn/html/can-bo-giang-vien",
    #            "https://sict.haui.edu.vn/vn/html/co-so-vat-chat", "https://sict.haui.edu.vn/vn/html/dia-chi-lien-he",
    #            "https://sict.haui.edu.vn/vn/html/khoa-hoc-may-tinh", "https://sict.haui.edu.vn/vn/html/ky-thuat-phan-mem",
    #            "https://sict.haui.edu.vn/vn/html/dai-hoc-he-thong-thong-tin", "https://sict.haui.edu.vn/vn/html/cong-nghe-thong-tin",
    #            "https://sict.haui.edu.vn/vn/html/cong-nghe-da-phuong-tien", "https://sict.haui.edu.vn/vn/html/an-toan-thong-tin",
    #            "https://sict.haui.edu.vn/vn/html/cao-hoc-he-thong-thong-tin"]
    
    # for link in weblink:
    #     indexing.indexing(input_path=link)