import os
import getpass
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import time

def retrieve(query):
  # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
  embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
  vector_store = Chroma(embedding_function=embeddings, persist_directory=r"E:\Data\chromadb\eb")


  from mxbai_rerank import MxbaiRerankV2
  rerank_model = MxbaiRerankV2("mixedbread-ai/mxbai-rerank-base-v2")

  start_time = time.time()
  docs = vector_store.similarity_search(query=query, k=35)

  # Create a dictionary to map text to full document objects
  doc_map = {doc.page_content: doc for doc in docs}
  # Extract just the text for reranking
  documents = [doc.page_content for doc in docs]

  # Perform reranking
  ranked_documents = rerank_model.rank(
      query=query,
      documents=documents,  # Only pass the text for ranking
      return_documents=True,
      top_k=5
  )

  context = []
  for text in ranked_documents:
    if text.document in doc_map:
      context.append(doc_map[text.document])
  docs_content = "\n\n".join(doc.page_content for doc in context)

  end_time = time.time()
  retrieve_time = end_time-start_time
  print("Retrieve done! Retrieve time: ", retrieve_time)

  return docs_content

query = "Kế hoạch phát bằng tốt nghiệp"
docs_content = retrieve(query=query)

st1 = time.time()
from langchain.prompts import PromptTemplate
# Define a Vietnamese prompt
prompt_template = """Bạn là một chatbot hỏi đáp thông minh. Hãy cung cấp câu trả lời chính xác dựa trên dữ liệu liên quan. Nếu bạn không biết câu trả lời, chỉ cần nói không biết. 
Phản hồi bằng tiếng Việt một cách tự nhiên, trình bày khoa học. Không lặp lại câu hỏi của người dùng.
Câu hỏi: {question}
Dữ liệu liên quan:
{context}
"""
prompt = PromptTemplate.from_template(prompt_template)


#LLM
from langchain_together import ChatTogether

from dotenv import load_dotenv
load_dotenv()

llm = ChatTogether(
  model="deepseek-ai/DeepSeek-V3",
  temperature=0,
  max_tokens=None,
  timeout=None
)

messages = prompt.invoke({"question":query, "context": docs_content})
response = llm.invoke(messages).content
et1 = time.time();
print(response)
print("Response time: ", et1-st1)