
from dotenv import load_dotenv
import os
load_dotenv()
from openai import OpenAI
import time
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb")

t1 = time.time()

question = "Thông tin về cơ cấu tổ chức"
top_docs = vector_store.similarity_search(query=question, k=3)
context = "\n\n".join(d.page_content for d in top_docs)
source = [d.metadata for d in top_docs]
message = f"""Câu hỏi: {question}
Dữ liệu liên quan:
{context}
"""
# print(message)


t2 = time.time()

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "Bạn là một chatbot thông minh chuyên hỗ trợ hỏi đáp chính xác dựa trên dữ liệu liên quan. Nếu bạn không biết câu trả lời, chỉ cần nói không biết. Trả lời tự nhiên, dễ hiểu, khoa học, mạch lạc. Không lặp lại câu hỏi, không trích dẫn dữ liệu."},
        {"role": "user", "content": message},
    ],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end='')

t3 = time.time()
print()
print(f"[RATE] Prompt length: {len(message)}")
print(f"[RATE] Vector search: {t2 - t1}")
print(f"[RATE] Response: {t3 - t2}")
print(f"[RATE] Total: {t3 - t1}")