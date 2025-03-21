# RAG indexing/ingestion pineline
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict

import os
import getpass

# LLM
if not os.environ.get("GROQ_API_KEY"):
  os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")
from langchain.chat_models import init_chat_model
llm = init_chat_model("llama3-8b-8192", model_provider="groq")

# Define prompt for question-answering
from langchain.prompts import PromptTemplate
# Define a Vietnamese prompt
prompt_template = """Bạn là một trợ lý AI thông minh chuyên hỗ trợ trả lời câu hỏi dựa trên tài liệu có sẵn.

Câu hỏi: {question}

Dữ liệu liên quan:
{context}

Dựa trên dữ liệu trên, hãy cung cấp một câu trả lời ngắn gọn và chính xác bằng tiếng Việt."""
prompt = PromptTemplate.from_template(prompt_template)

response = llm.invoke(prompt,{"question": "Trường có tất cả bao nhiêu người?"})
print(response["answer"])