import json
import spacy
import os

from lxml import etree

nlp = spacy.load("en_core_web_sm")

class JsonConverter():
    def __init__(self, file_path):
        self.namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}

        self.tree = etree.parse(file_path)
        self.root = self.tree.getroot()
    
        self.base_filename = file_path.split('/')[-1].split('.')[0]

    def get_data(self):
        title = self.get_title()
        authors = self.get_authors()
        doi = self.get_doi()
        sections = self.get_sections()

        article_data = {
            "article_id": self.base_filename,
            "title": title,
            "doi": doi,
            "authors": authors,
            "sections": sections
        }

        return article_data
    
    def save_as_json(self, filename=None):
        if not filename:
            filename = f'./data/clean/{self.base_filename}.json'
        
        article_data = self.get_data()

        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(article_data, json_file, ensure_ascii=False, indent=4)

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

            chunks = self.chunk_text(text, title)
            sections.extend(chunks)

        return sections
    
    def chunk_text(self, text, section_title):
        doc = nlp(text)
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
                        "source_doi": self.get_doi()
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
                "source_doi": self.get_doi()
            })

        return chunks
    
    def clean_text(self, text):
        return " ".join(text).strip().replace("\n", " ").replace("  ", " ")

    def validate_data(self, id):
        data = self.get_data()

        errors = []

        def add_error(article_id, error_message):
            article_error = next((item for item in errors if item['article_id'] == article_id), None)
            if article_error:
                article_error['errors'].append(error_message)
            else:
                errors.append({
                    "article_id": article_id,
                    "errors": [error_message]
                })

        title = data.get("title")
        if not self.validate_list(title, str):
            add_error(data['article_id'], "Missing or invalid title")

        doi = data.get("doi")
        if not self.validate_list(doi, str):
            add_error(data['article_id'], "Missing or invalid DOI")

        sections = data.get("sections")
        if not self.validate_list(sections, dict):
            add_error(data['article_id'], "Missing or invalid sections")
        else:
            valid_sections = [section for section in sections if len(section['text'].strip()) > 300]
            if len(valid_sections) < 3:
                add_error(data['article_id'], "Article must have at least 3 valid sections")

            for section in sections:
                if len(section['text'].strip()) < 300:
                    add_error(data['article_id'], f"Section '{section['section']}' has less than 300 characters")

        return errors

    def validate_list(self, data, expected_type):
        if isinstance(data, list) and all(isinstance(item, expected_type) for item in data):
            return True
        return False

def process_files_in_directory(directory_path):
    os.makedirs('./data/clean', exist_ok=True)

    for index, filename in enumerate(os.listdir(directory_path)):
        if filename.endswith('.xml'):
            file_path = os.path.join(directory_path, filename)
            print(f'Processing file: {filename}')

            xml_converter = JsonConverter(file_path)
            xml_converter.save_as_json()
            xml_converter.validate_data(index) 

if __name__ == '__main__':
    xml_directory = './data/processed'
    process_files_in_directory(xml_directory)