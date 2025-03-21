from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import bs4

# Select embedding models
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Vector store
from langchain_chroma import Chroma
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb")

# Load and chunk contents of the blog
loader = WebBaseLoader(
    web_paths=("https://sict.haui.edu.vn/vn/html/bo-may-to-chuc","https://sict.haui.edu.vn/vn/html/thong-tin-chung"),
    # bs_kwargs=dict(
    #     parse_only=bs4.SoupStrainer(
    #         class_=("post-content", "post-title", "post-header")
    #     )
    # ),
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
all_splits = text_splitter.split_documents(docs)

# Index chunks
_ = vector_store.add_documents(documents=all_splits)

print("Ingestion data done!")