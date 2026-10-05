from app.rag.chunking.text_chunker import TextChunker

text = """
Retrieval Augmented generation combines imformation
retrieval with large language models to create a powerful tool for
generating accurate and relevant responses. It allows LLMs to access external knowledge sources, such as databases, documents, or APIs, to retrieve relevant information and incorporate it into their responses. This approach enhances the capabilities of LLMs by providing them with up-to-date and domain-specific knowledge, enabling them to generate more accurate and contextually appropriate answers.
The process of retrieval augmented generation typically involves two main steps: retrieval and generation. In the retrieval step, the system identifies relevant information from external sources based on the input query or context. This can be done using various techniques, such as keyword matching, semantic search, or vector-based retrieval methods. Once the relevant information is retrieved, it is passed to the generation step, where the LLM utilizes this information to generate a response that incorporates the retrieved knowledge.
The benefits of retrieval augmented generation are numerous. It allows LLMs to provide more accurate and contextually relevant responses, especially in domains where up-to-date information is crucial. It also enables LLMs to handle queries that require specific knowledge or expertise, as they can access external sources to supplement their understanding. Additionally, retrieval augmented generation can help mitigate the limitations of LLMs, such as their tendency to generate plausible-sounding but incorrect information, by grounding their responses in verified external knowledge.
Overall, retrieval augmented generation represents a significant advancement in the field of natural language processing and has the
"""

chunker = TextChunker(
    chunk_size=100,
    chunk_overlap=10
)

chunks = chunker.chunk(text)

print("Number of chunks: ", len(chunks))

for index, chunk in enumerate(chunks):
    print(f"Chunk {index + 1}:")
    print(chunk)
    print("-" * 50)