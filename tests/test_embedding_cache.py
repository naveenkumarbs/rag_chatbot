from app.rag.embeddings.ollama_provider import OllamaEmbeddingProvider

provider = OllamaEmbeddingProvider()

query = (
    "What is the resolution "
    "from the partners meeting?"
)

print ("FIRST CALL")

embedding_1 = provider.embed_text(query)

print ("Embedding dimension: ", len(embedding_1))

print("\nSECOND CALL")

embedding_2 = provider.embed_text(query)

print ("Embedding dimension:", len(embedding_2))

print ("\nSame embedding:", embedding_1 == embedding_2)
