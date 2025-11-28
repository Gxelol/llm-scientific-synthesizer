class ArticleRetriever:
    def __init__(self, articles_json):
        self.articles_json = articles_json

    def retrieve_relevant_sections(self, indices):
        relevant_sections = []
        for idx in indices:
            article = self.articles_json[idx] 
            for section in article['sections']:
                relevant_sections.append(section['text'])
        return relevant_sections