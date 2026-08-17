import os
import chromadb
from typing import List, Dict, Any

class MemoryManager:
    def __init__(self, persist_dir: str = "./data/chroma_db", collection_name: str = "headline_memory"):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def save(self, doc_id: str, text: str, metadata: Dict[str, Any]):
        clean_meta = {k: str(v) if not isinstance(v, (str, int, float, bool)) else v for k, v in metadata.items()}
        self.collection.upsert(
            documents=[text],
            metadatas=[clean_meta],
            ids=[doc_id]
        )

    def recall(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        count = self.collection.count()
        if count == 0:
            return []
        k = min(top_k, count)
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )
        memories = []
        if results and results.get("documents"):
            for i in range(len(results["documents"][0])):
                memories.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i]
                })
        return memories

    def clear(self):
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(name=self.collection.name)