from app.rag.embeddings.ollama_provider import OllamaEmbeddingProvider

provider = OllamaEmbeddingProvider()

texts = [
    "This is document one.",
    "This is document two.",
    "This is document three."
]

embeddings = provider.embed_documents(texts)
print ("Inputs: ", len(texts))
print ("Embeddings: ", len(embeddings))

for index, embedding in enumerate(embeddings):
    print (
        index,
        embedding, 
        len(embedding)
    )