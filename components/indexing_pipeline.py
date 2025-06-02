import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def indexing(input_path, language=None, text_splitter=None, embeddings_model=None, stored_path=None):
    """
    Indexing and save document for indexing/ingestion pineline.

    Args:
        input_path (string): A file or link to load document.
        text_splitter (TextSplitter): A model to split documents to chunks.
        embeddings (EmbeddingModel): An embedding model to embed chunks. 
        stored_path (string): A persist directory for saving vector in chromadb.
    
    Returns:
        None
    """
    if language is None:
        language = "eng"
    docs = load_document(input=input_path, language=language)
    if docs == []:
        print("No documents for indexing!")
        return
    print("[INFO] Data is being ingested...")

    if text_splitter is None:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    if embeddings_model is None:
        embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")  #384 dim
    if stored_path is None:
        stored_path = r"E:\Data\chromadb"

    vector_store = Chroma(embedding_function=embeddings_model, persist_directory=stored_path)
    all_splits = text_splitter.split_documents(docs)
    _ = vector_store.add_documents(documents=all_splits)

    print(f"[SUCCESS] Ingested {len(all_splits)} chunks. Data saved to: {stored_path}")


from langchain_community.document_loaders import (
    WebBaseLoader, UnstructuredPDFLoader, UnstructuredWordDocumentLoader, UnstructuredCSVLoader, UnstructuredExcelLoader,
    UnstructuredPowerPointLoader, BSHTMLLoader, TextLoader, JSONLoader
)

from youtube_transcript_api import YouTubeTranscriptApi
from langchain.schema import Document

def load_document(input, language="eng"):
    """
    Define which type of input.
    """
    if input is None or input == "":
        return []
    if input.startswith("https://www.youtube.com"):
        return load_audio_video(link=input)
    elif input.startswith("http://") or input.startswith("https://"):
        return load_weblink(link=input)
    else:
        return load_file(file_path=input, language=language)


def load_file(file_path, language="eng"):
    """
    Extract list of document from file.

    Args:
        input_path (string): file path.
    Returns:
        List[Documents]: list of documents.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = UnstructuredPDFLoader(file_path, strategy="hi_res", languages=[language])
    elif ext == ".docx":
        loader = UnstructuredWordDocumentLoader(file_path, strategy="hi_res", languages=[language])
    elif ext == ".pptx":
        loader = UnstructuredPowerPointLoader(file_path, strategy="hi_res", languages=[language])
    elif ext == ".html":
        loader = BSHTMLLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    elif ext == ".csv":
        loader = UnstructuredCSVLoader(file_path=file_path)
    elif ext == ".json":
        loader = JSONLoader(file_path=file_path, jq_schema=".content", text_content=False)
    elif ext == ".xlsx" or ext == ".xls":
        loader = UnstructuredExcelLoader(file_path=file_path)
    else:
        print("Unsupported file format:", ext)
        return []

    return loader.load()
    

def load_weblink(link=None):
    """
    Extract documents from website.
    """
    loader = WebBaseLoader(web_paths=([link]), encoding="UTF-8")
    return loader.load()

def load_audio_video(link=None):
    """
    Extract documents from video/youtube.
    """
    try:
        video_id = link.split("v=")[1]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=("en", "vi"))
        doc = " ".join(snippet["text"] for snippet in transcript_list)

        docs = []
        docs.append(Document(page_content=doc, metadata={"source": link}))
        return docs
    except Exception as e:
        print(f"Error loading YouTube video: {e}")
        return []