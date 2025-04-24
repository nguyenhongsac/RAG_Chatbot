from components.rag_pipeline import RAGService

async def main():
  rag = RAGService()
  result = await rag.ask("Ai là hiệu trưởng?")
  print("Answer:", result["answer"])
  print("Sources:", result["sources"])

import asyncio
if __name__ == "__main__":
  asyncio.run(main())