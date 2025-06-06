from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import components.indexing_pipeline as indexing_pipeline

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb1")

# vector_store.delete(ids="")

if __name__ == "__main__":

    # path = r"E:\Data\File\pdf"
    path = r"E:\Data\File\html"
    for f in os.listdir(path=path):
        file_path = path + '/' + f
        indexing_pipeline.indexing(input_path=file_path, language="vie", stored_path=r"E:\Data\chromadb1")

    # weblink = ["https://sict.haui.edu.vn/vn/html/thong-tin-chung", 
    #            "https://sict.haui.edu.vn/vn/html/bo-may-to-chuc",
    #            "https://sict.haui.edu.vn/vn/html/chien-luoc-phat-trien", 
    #            "https://sict.haui.edu.vn/vn/html/can-bo-giang-vien",
    #            "https://sict.haui.edu.vn/vn/html/co-so-vat-chat", 
    #            "https://sict.haui.edu.vn/vn/html/dia-chi-lien-he",
    #            "https://sict.haui.edu.vn/vn/html/khoa-hoc-may-tinh", 
    #            "https://sict.haui.edu.vn/vn/html/ky-thuat-phan-mem",
    #            "https://sict.haui.edu.vn/vn/html/dai-hoc-he-thong-thong-tin", 
    #            "https://sict.haui.edu.vn/vn/html/cong-nghe-thong-tin",
    #            "https://sict.haui.edu.vn/vn/html/cong-nghe-da-phuong-tien", 
    #            "https://sict.haui.edu.vn/vn/html/an-toan-thong-tin",
    #            "https://sict.haui.edu.vn/vn/html/cao-hoc-he-thong-thong-tin"]
    
    # for link in weblink:
    #     indexing_pipeline.indexing(input_path=link, stored_path=r"E:\Data\chromadb1")