class SemanticSearch:
    def __init__(self, faiss_index, embedding_generator):
        self.faiss_index = faiss_index
        self.embedding_generator = embedding_generator

    def search(self, query, top_k=5):
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        distances, indices = self.faiss_index.semantic_search(query_embedding, top_k)
        
        return distances, indices