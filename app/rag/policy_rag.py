from pathlib import Path
import re

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction


class PolicyRAG:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="data/chroma")
        self.embedding_function = DefaultEmbeddingFunction()

        self.full_collection = self.client.get_or_create_collection(
            name="nykaa_policies_full",
            embedding_function=self.embedding_function
        )

        self.chunk_collection = self.client.get_or_create_collection(
            name="nykaa_policies_chunks",
            embedding_function=self.embedding_function
        )

    def build_index(self):
        policy_files = sorted(Path("data/policies").glob("*.txt"))

        if not policy_files:
            raise FileNotFoundError("No policy documents found.")

        full_ids = []
        full_documents = []
        full_metadata = []

        chunk_ids = []
        chunk_documents = []
        chunk_metadata = []

        for file in policy_files:
            content = file.read_text(encoding="utf-8").strip()

            full_ids.append(file.stem)
            full_documents.append(content)
            full_metadata.append({"source": file.name})

            sentences = [
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", content)
                if sentence.strip()
            ]

            for index, sentence in enumerate(sentences):
                chunk_ids.append(f"{file.stem}_{index}")
                chunk_documents.append(sentence)
                chunk_metadata.append({
                    "source": file.name,
                    "chunk_index": index
                })

        self.full_collection.upsert(
            ids=full_ids,
            documents=full_documents,
            metadatas=full_metadata
        )

        self.chunk_collection.upsert(
            ids=chunk_ids,
            documents=chunk_documents,
            metadatas=chunk_metadata
        )

        return {
            "full_documents": len(full_ids),
            "sentence_chunks": len(chunk_ids)
        }

    def search(self, query, strategy="full", limit=3):
        if strategy not in {"full", "chunks"}:
            raise ValueError("Strategy must be 'full' or 'chunks'.")

        collection = (
            self.full_collection
            if strategy == "full"
            else self.chunk_collection
        )

        count = collection.count()

        if count == 0:
            return []

        results = collection.query(
            query_texts=[query],
            n_results=min(limit, count)
        )

        matches = []

        for document, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            matches.append({
                "text": document,
                "source": metadata["source"],
                "distance": round(float(distance), 4)
            })

        return matches
