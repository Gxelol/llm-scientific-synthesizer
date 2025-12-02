import faiss
import numpy as np

class FAISSIndex:
    def __init__(self, embeddings):
        self.index = None
        self.create_index(embeddings)

    def create_index(self, embeddings):
        dimension = len(embeddings[0])
        self.index = faiss.IndexFlatL2(dimension)
        embeddings = np.array(embeddings).astype('float32')
        self.index.add(embeddings)

    def semantic_search(self, query_embedding, top_k=5):
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, top_k)
        return distances, indices