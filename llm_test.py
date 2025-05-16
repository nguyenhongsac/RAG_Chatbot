
from dotenv import load_dotenv
import os
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb")

question = "Hiệu trưởng là ai?"
top_docs = vector_store.similarity_search(query=question, k=5)

context = "\n\n".join(d.page_content for d in top_docs)
source = [d.metadata for d in top_docs]
message = f"""Câu hỏi: {question}
Dữ liệu liên quan:
{context}
"""
print(message)

from openai import OpenAI

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "Bạn là một chatbot hỏi đáp thông minh. Hãy trả lời chính xác dựa trên dữ liệu liên quan. Nếu bạn không biết câu trả lời, chỉ cần nói không biết. Không lặp lại câu hỏi."},
        {"role": "user", "content": message},
    ],
    stream=False
)

print(response.choices[0].message.content)