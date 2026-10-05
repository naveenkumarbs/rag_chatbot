from app.rag.providers.ollama_provider import OllamaLLMProvider

class QueryRewriter:
    def __init__(self):
        self.llm = OllamaLLMProvider()

    def rewrite(self, question: str, history: list[dict])->str:
        if not history:
            return question

        history_text = "\n".join(
            f"{item['role']}: {item['content']}" for item in history
        )

        prompt = f"""
        Rewrite the latest user question into a standalone search query.
        Use te conversation history only to resolve references such as "it", "that", "they", "the account", etc.

        Do not answer the question.

        If the question is already standalone, return it unchanged.

        CONVERSATION:
        {history_text}

        LATEST QUESTION:
        {question}

        STANDALONE QUERY:
        """.strip()

        rewritten = self.llm.generate(prompt)

        return rewritten.strip()
    