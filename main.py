import json
import spacy
import os

from lxml import etree

nlp = spacy.load("en_core_web_sm")

class XmlParser:
    def __init__(self, file_path):
        self.tree = etree.parse(file_path)
        self.root = self.tree.getroot()
        self.namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    def get_title(self):
        return self.root.xpath('//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[@type="main"]/text()', namespaces=self.namespaces)

    def get_doi(self):
        return self.root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:idno[translate(@type, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="doi"]/text()', namespaces=self.namespaces)

    def get_authors(self):
        authors = []
        author_path = '//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:analytic/tei:author'

        for author in self.root.xpath(author_path, namespaces=self.namespaces):
            persName = author.find('tei:persName', namespaces=self.namespaces)
            
            if persName is not None:
                first_name = persName.find('tei:forename[@type="first"]', namespaces=self.namespaces)
                middle_name = persName.find('tei:forename[@type="middle"]', namespaces=self.namespaces)
                surname = persName.find('tei:surname', namespaces=self.namespaces)
                
                email_elem = author.find('tei:email', namespaces=self.namespaces)
                email = email_elem.text if email_elem is not None else None

                authors.append({
                    "first_name": first_name.text if first_name is not None else None,
                    "middle_name": middle_name.text if middle_name is not None else None,
                    "surname": surname.text if surname is not None else None,
                    "email": email
                })

        return authors

    def get_sections(self):
        sections = []

        section_path = '//tei:text/tei:body/tei:div'

        for section in self.root.xpath(section_path, namespaces=self.namespaces):

            head = section.find('tei:head', namespaces=self.namespaces)
            title = head.text if head is not None else ''
        
            paragraphs = section.findall('tei:p', namespaces=self.namespaces)
            text = ' '.join([''.join(p.itertext()) for p in paragraphs])

            sections.append({
                "section_title": title,
                "text": text
            })
            
        return sections

class TextProcessor:
    def __init__(self, nlp):
        self.nlp = nlp

    def chunk_text(self, text, section_title, doi):
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]

        chunk_id = 1
        chunk_size = 0
        chunk_text = []
        chunks = []

        for sentence in sentences:
            token_count = len(sentence.split())

            if chunk_size + token_count > 500:
                if chunk_text:
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_id:03}",
                        "section": section_title,
                        "text": " ".join(chunk_text),
                        "source_doi": doi
                    })
                    chunk_id += 1
                chunk_text = [sentence]
                chunk_size = token_count
            else:
                chunk_text.append(sentence)
                chunk_size += token_count

        if chunk_text:
            chunks.append({
                "chunk_id": f"chunk_{chunk_id:03}",
                "section": section_title,
                "text": " ".join(chunk_text),
                "source_doi": doi
            })
        
        if len(chunks) > 1 and len(chunks[-1]["text"].split()) < 100:
            last_chunk = chunks.pop()  # Remove o último chunk
            chunks[-1]["text"] += " " + last_chunk["text"]  # Adiciona ao penúltimo

        return chunks
    
class DataValidator:
    def __init__(self, article_data):
        self.article_data = article_data

    def validate_data(self):
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
            valid_sections = [section for section in sections if len(section['text'].strip()) > 300]
            if len(valid_sections) < 1:
                add_error("Article must have at least 1 valid section")

            for section in sections:
                if len(section['text'].strip()) < 300:
                    add_error(f"Section '{section['text']}' has less than 300 characters")

        return errors

    def validate_list(self, data, expected_type):
        if isinstance(data, list) and all(isinstance(item, expected_type) for item in data):
            return True
        return False

    def validate_chunks(self, chunks):
        errors = []
        seen_texts = set()

        for chunk in chunks:
            text = chunk.get("text", "").strip()

            if not text:
                errors.append(f"Chunk {chunk['chunk_id']} is empty")
                continue

            if len(text) < 300:
                errors.append(f"Chunk {chunk['chunk_id']} is too short (less than 300 characters)")
            
            if text in seen_texts:
                errors.append(f"Chunk {chunk['chunk_id']} is duplicated")
            else:
                seen_texts.add(text)

        return errors
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
        for section in sections:
            chunks = self.text_processor.chunk_text(section['text'], section['section_title'], doi)
            all_chunks.extend(chunks)

        article_data = {
            "article_id": self.base_filename,
            "title": title,
            "doi": doi,
            "authors": authors,
            "sections": all_chunks
        }

        return article_data
    
    def save_as_json(self, filename=None):
        if not filename:
            filename = f'./data/clean/{self.base_filename}.json'
        
        article_data = self.get_data()

        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(article_data, json_file, ensure_ascii=False, indent=4)
    
    def generate_validation_report(self, articles):
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

            data_validator = DataValidator(article_data)  # Cria uma instância do validador
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
        if not filename:
            filename = f'./data/validation_report.json'

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(report, file, ensure_ascii=False, indent=4)

def process_files_in_directory(directory_path, nlp):
    os.makedirs('./data/clean', exist_ok=True)

    articles = []

    for filename in os.listdir(directory_path):
        if filename.endswith('.xml'):
            file_path = os.path.join(directory_path, filename)
            print(f'Processing file: {filename}')

            xml_converter = JsonConverter(file_path, nlp)
            xml_converter.save_as_json()
            articles.append(xml_converter)

    report = xml_converter.generate_validation_report(articles)
    xml_converter.save_validation_report(report)

if __name__ == '__main__':
    xml_directory = './data/processed'
    process_files_in_directory(xml_directory, nlp)