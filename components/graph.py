from langgraph.graph import START, StateGraph
from typing import List, TypedDict
from langchain_core.documents import Document

from components.init_models import vector_store, rerank_model, llm
from components.prompts import prompt

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

graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()