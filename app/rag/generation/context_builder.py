class ContextBuilder:
    def build(
            self,
            retrieved_chunks: list[dict]
    ) -> str:

        sections = []

        for index, item in enumerate(
            retrieved_chunks,
            start=1
        ):
            source = item["metadata"]["filename"]
            chunk_index = item["metadata"]["chunk_index"]

            section = (
                f"[(Source: {index}\n "
                f"File: {source}\n"
                f"{item['text']}"
            )
            sections.append(section)

        return "\n\n---\n\n".join(sections)