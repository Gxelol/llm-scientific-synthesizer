# Define a class for validating the extracted data
class DataValidator:
    def __init__(self, article_data):
        self.article_data = article_data

    def validate_data(self):
        # Validate the main article data (title, DOI, sections, etc.)
        errors = []

        def add_error(error_message):
            errors.append(error_message)

        title = self.article_data.get("title")
        if not self.validate_list(title, str):
            add_error("Missing or invalid title")

        doi = self.article_data.get("doi")
        if not self.validate_list(doi, str):
            add_error("Missing or invalid DOI")

        sections = self.article_data.get("sections")
        if not self.validate_list(sections, dict):
            add_error("Missing or invalid sections")
        else:
            valid_sections = [section for section in sections if len(section['text'].strip()) > 200]
            if len(valid_sections) < 1:
                add_error("Article must have at least 1 valid section")

            for section in sections:
                if len(section['text'].strip()) < 200:
                    add_error(f"Section '{section['text']}' has less than 200 characters")

        return errors

    def validate_list(self, data, expected_type):
        if isinstance(data, list) and all(isinstance(item, expected_type) for item in data):
            return True
        return False

    def validate_chunks(self, chunks):
        # Validate the chunks of text 
        errors = []
        seen_texts = set()

        for chunk in chunks:
            text = chunk.get("text", "").strip()

            if not text:
                errors.append(f"Chunk {chunk['chunk_id']} is empty")
                continue

            if len(text) < 200:
                errors.append(f"Chunk {chunk['chunk_id']} is too short (less than 200 characters)")
            
            if text in seen_texts:
                errors.append(f"Chunk {chunk['chunk_id']} is duplicated")
            else:
                seen_texts.add(text)

        return errors