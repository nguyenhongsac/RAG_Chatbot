from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.responses import StreamingResponse
from components.rag_pipeline import RAGService
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import logging

# Run with base pipeline

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific domains for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)
# async def get_api_key(api_key: str = Security(api_key_header)):
#     if api_key != Settings.API_KEY:
#         logger.warning("Invalid API key: %s", api_key)
#         raise HTTPException(403, "Invalid API key")
#     return api_key

rag = RAGService()

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: list

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    try:
        return ChatResponse(**await rag.ask(req.question))
    except Exception:
        logging.exception("chat error")
        raise HTTPException(500, "Internal Server Error")

@app.post("/chat-stream")
async def chat_stream(req: ChatRequest):
    return StreamingResponse(
        rag.ask_stream(req.question),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)