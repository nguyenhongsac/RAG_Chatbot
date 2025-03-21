# RAG indexing/ingestion pineline
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

import os
import getpass

#Viet nghia tung doan 

# LLM
if not os.environ.get("GROQ_API_KEY"):
  os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")
from langchain.chat_models import init_chat_model
llm = init_chat_model("llama3-8b-8192", model_provider="groq")

# Select embedding models
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Vector store
from langchain_chroma import Chroma
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb")

# Define prompt for question-answering
from langchain.prompts import PromptTemplate
# Define a Vietnamese prompt
prompt_template = """Bạn là một trợ lý để trả lời câu hỏi. Sử dụng các phần thông tin đã truy xuất sau để trả lời câu hỏi. 
Nếu không biết câu trả lời, chỉ cần nói rằng bạn không biết. Chỉ cần đưa ra câu trả lời bằng tiếng Việt.

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
    retrieved_docs = vector_store.similarity_search(query=state["question"], k=7)
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

# # test
# response = graph.invoke({"question": "ai là hiệu trưởng trường công nghệ thông tin và truyền thông"})

# print(f'Context: {response["context"]}\n\n')
# print(f'Answer: {response["answer"]}')

# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))


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
# uvicorn {your_script_name}:app --reload