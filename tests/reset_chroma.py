import chromadb

from app.core.config import settings

client = chromadb.PersistentClient(
    path=settings.chroma_db_path
)

collection_name = settings.chroma_collection 

try:
    client.delete_collection(
        name=collection_name
    )

    print (
        f"Deleted collection:  {collection_name} "
    )

except Exception as exc:
    print (
        f"Collection may not exist yet: {exc}"
    )

collection = client.get_or_create_collection(
    name=collection_name
)

print(
    f"Created clean collection: {collection.name}"
)
