# RAG indexing/ingestion pineline
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

import os
import getpass


from dotenv import load_dotenv
load_dotenv()

# LLM
'''
> Enter groq API to get available LLM models (change LLM model later).
> Use init_chat_model from langchain to init that llm model as chatbot.
'''
from langchain_together import ChatTogether
llm = ChatTogether(
    model="deepseek-ai/DeepSeek-V3",
    temperature=0,
    max_tokens=None,
    timeout=None
  )


# Select embedding models
'''
> Init embedding model - same as indexing pineline.
'''
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2") # 384 dim


# Vector store
'''
> Init vector store (use Chroma here).
'''
from langchain_chroma import Chroma
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb")

# Rerank model
'''
> Use for rerank document after using similar_search, get top 5 from 35.
> Enhance accuracy of retriever
'''
from mxbai_rerank import MxbaiRerankV2
rerank_model = MxbaiRerankV2("mixedbread-ai/mxbai-rerank-base-v2")

# Define prompt for question-answering
'''
> Set prompt for better response.
'''
from langchain.prompts import PromptTemplate
# Define a Vietnamese prompt
prompt_template = """Bạn là một chatbot hỏi đáp thông minh. Hãy cung cấp câu trả lời chính xác dựa trên dữ liệu liên quan. Nếu bạn không biết câu trả lời, chỉ cần nói không biết. 
Phản hồi bằng tiếng Việt một cách tự nhiên, trình bày khoa học. Không lặp lại câu hỏi của người dùng. Không bắt đầu bằng "Theo thông tin được cung cấp", "Theo dữ liệu được cung cấp".
Câu hỏi: {question}

Dữ liệu liên quan:
{context}
"""
prompt = PromptTemplate.from_template(prompt_template)


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# Define application steps
def retrieve(state: State):
    docs = vector_store.similarity_search(query=state["question"], k=30)

    # Create a mapping from page_content to full document to return metadata after reranking
    doc_map = {doc.page_content: doc for doc in docs}
    documents = [doc.page_content for doc in docs]

    rankeds = rerank_model.rank(
        query=state["question"],
        documents=documents,  # Only pass text
        return_documents=True,
        top_k=5
    )

    retrieved_docs = []
    for text in rankeds:
        if text.document in doc_map:
            retrieved_docs.append(doc_map[text.document])


    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# # test
# response = graph.invoke({"question": "ai là hiệu trưởng trường công nghệ thông tin và truyền thông"})
# print(f'Context: {response["context"]}\n\n')
# print(f'Answer: {response["answer"]}')
# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))

# Deloy through FastAPI
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific domains for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define a model for incoming chat requests
class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # Invoke the graph with the question
    response = graph.invoke({"question": request.question})
    return {"answer": response["answer"]}

# To run:
# uvicorn {script_name}:app --reload (uvicorn llm:app --reload)