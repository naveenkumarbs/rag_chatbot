from app.rag.embeddings.ollama_provider import (
    OllamaEmbeddingProvider
)

provider = OllamaEmbeddingProvider()

embedding = provider.embed_text(
    "Artificial Intelligence helps automate tasks."
)

print ("Embedding dimension:   ", len(embedding))
print ("First 10 values of embedding: ", embedding[:10])