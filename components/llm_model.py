from openai import OpenAI

class DeepSeekLLM():
    """
    A custom llm class
    """
    prompt_template = "Bạn là một chatbot hỏi đáp thông minh. Hãy trả lời chính xác dựa trên dữ liệu liên quan. Nếu bạn không biết câu trả lời, chỉ cần nói không biết. Không lặp lại câu hỏi."

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    def invoke(self, message: str) -> str:
        """
        Message includes {question} and {context}
        """

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": message},
            ],
            stream=False
        )

        return response.choices[0].message.content
    
    async def ainvoke(self, message: str):
        """
        Response in stream mode
        """
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.prompt_template},
                {"role": "user", "content": message},
            ],
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content