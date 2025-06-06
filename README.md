# RAG_Chatbot
Link for back_end test: https://github.com/nguyenhongsac/Chatbot_Backend

This is a custom RAG chatbot.
Indexing:
    1. Loading: from langchain
    2. Document splitting: RecursiveCharacterTextSplitter from langchain
    3. Embedding: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 from HuggingFace
    4. VectorDB: Chroma from langchain.
RAG:
    - Retriever: similar search + rerank
    *Rerank model: AITeamVN/Vietnamese_Reranker from HuggingFace
    - LLM: DeepSeek-V3 via API (DeepSeekV3-Chat)