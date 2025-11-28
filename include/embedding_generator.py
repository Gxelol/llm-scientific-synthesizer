import json
import torch

from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    def __init__(self, model_name="allenai/specter2_base"):
        self.model = SentenceTransformer(model_name, device='cpu')
    
    def generate_embedding(self, text):
        return self.model.encode(text)
    
    def process_articles(self, articles_json):
        embeddings = []
        locations = []
        
        for article in articles_json:
            article_id = article['article_id']
            for i, section in enumerate(article['sections']):
                embedding = self.generate_embedding(section['text'])
                embeddings.append(embedding)
                locations.append((article_id, i))
        
        return embeddings, locations
