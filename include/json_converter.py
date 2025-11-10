import json

from .data_validator import DataValidator
from .text_processor import TextProcessor
from .xml_parser     import XmlParser

# Define a class to convert XML data to JSON format
class JsonConverter:
    def __init__(self, file_path, nlp):
        self.xml_parser = XmlParser(file_path)
        self.text_processor = TextProcessor(nlp)
        self.base_filename = file_path.split('/')[-1].split('.')[0]

    def get_data(self):
        title = self.xml_parser.get_title()
        authors = self.xml_parser.get_authors()
        doi = self.xml_parser.get_doi()
        sections = self.xml_parser.get_sections()

        all_chunks = []
        irrelevant_section = []

        # Process each section, chunk its text, and add it to json
        for section in sections:
            if self.is_section_too_short(section) == True:
                irrelevant_section.append(section)
                continue
            
            chunks = self.text_processor.chunk_text(section['text'], section['section_title'], doi)
            all_chunks.extend(chunks)

        # JSON output
        article_data = {
            "article_id": self.base_filename,
            "title": title,
            "doi": doi,
            "authors": authors,
            "sections": all_chunks
        }

        return article_data
    
    def is_section_too_short(self, section):
        """
        Checks if the section is too short to be relevant for the language model.

        Some XML files may contain non-relevant content within the <body> tag, such as glossaries 
        or appendices, which get captured along with the main sections. This function filters out 
        sections with insufficient text (less than 30 words or 100 meaningful characters), removing 
        parts that are not relevant for language model processing.
        """
        text = section['text']

        if len(text.split()) < 30 or len(text.strip()) < 100:
            return True
        
        return False

    def save_as_json(self, filename=None):
        # Save the data as a JSON file
        if not filename:
            filename = f'./data/clean/{self.base_filename}.json'
        
        article_data = self.get_data()

        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(article_data, json_file, ensure_ascii=False, indent=4)
    
    def generate_validation_report(self, articles):
        # Generate a report on the validation of data
        report = {
            "total_articles": len(articles),
            "valid_articles": 0,
            "failed_parsing": 0,
            "total_chunks": 0,
            "avg_chars_per_chunk": 0,
            "errors": []
        }

        total_chunks = 0
        total_chars = 0

        for article in articles:
            article_data = article.get_data()

            data_validator = DataValidator(article_data)
            article_errors = data_validator.validate_data()

            chunk_errors = data_validator.validate_chunks(article_data['sections'])
            article_errors.extend(chunk_errors)

            for section in article_data["sections"]:
                total_chunks += 1
                total_chars += len(section.get("text", "").strip())

            if article_errors:
                report["failed_parsing"] += 1
                report["errors"].append({
                    "article_id": article_data["article_id"],
                    "errors": article_errors
                })
            else:
                report["valid_articles"] += 1

        if total_chunks > 0:
            report["avg_chars_per_chunk"] = total_chars / total_chunks

        return report
    
    def save_validation_report(self, report, filename=None):
        # Save a report on the validation of data
        if not filename:
            filename = f'./data/validation_report.json'

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(report, file, ensure_ascii=False, indent=4)