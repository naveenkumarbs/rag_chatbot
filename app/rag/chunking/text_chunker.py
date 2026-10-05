class TextChunker:

    def __init__(
            self,
            chunk_size: int = 500,
            chunk_overlap: int = 200
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text:str) -> list[str]:
        text = text.strip()

        if not text:
            return []
        
        chunks = []

        start = 0

        while (start < len(text)):
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start += (
                self.chunk_size - self.chunk_overlap
            )

        return chunks

        
