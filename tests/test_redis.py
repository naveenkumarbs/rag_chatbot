from app.core.redis_client import redis_client

print("Redis ping:" , redis_client.ping())

redis_client.set("rag:test","Redis working", ex=60)

print ("Redis value:", redis_client.get("rag:test"))
