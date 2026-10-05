import chromadb

client = chromadb.PersistentClient(path="./data/chroma")

print("Chroma heartbeat:", client.heartbeat())

collection = client.get_or_create_collection(
    name="environment_test"
)

print("Collection:", collection.name)
print("Chroma environment OK")