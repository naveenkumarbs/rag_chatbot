from app.rag.providers.ollama_provider import OllamaLLMProvider

provider = OllamaLLMProvider()

response = provider.generate(
    "Explain RAG in two sentences."
)

print ("Response: ", repr(response))