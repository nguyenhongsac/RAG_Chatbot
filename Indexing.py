from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import bs4
from langchain_chroma import Chroma

def indexing(loader, embeddings, stored_path):
    """
    """
    # Vector store
    vector_store = Chroma(embedding_function=embeddings, persist_directory=stored_path)

    # Loading
    docs = loader.load()

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    all_splits = text_splitter.split_documents(docs)

    # Index chunks
    _ = vector_store.add_documents(documents=all_splits)

# Select embedding models
from langchain_huggingface import HuggingFaceEmbeddings
# embeddings1 = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2") #768 dim
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") #384 dim

stored_path = r"E:\Data\chromadb\eb"

# Load and chunk contents of the blog
loader = WebBaseLoader(
    web_paths=("https://sict.haui.edu.vn/vn/html/bo-may-to-chuc","https://sict.haui.edu.vn/vn/html/thong-tin-chung"),
    # bs_kwargs=dict(
    #     parse_only=bs4.SoupStrainer(
    #         class_=("post-content", "post-title", "post-header")
    #     )
    # ),
)

indexing(loader=loader, embeddings=embeddings, stored_path=stored_path)

print("Ingestion data done!")