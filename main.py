import json
import pandas as pd

from lxml import etree

class JsonConverter():
    def __init__(self, file_path):
        self.namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}

        self.tree = etree.parse(file_path)
        self.root = self.tree.getroot()
    
        self.base_filename = file_path.split('/')[-1].split('.')[0]

    def extract_field(self, xpath_expr, default_value='', multiple=False):
        values = self.root.xpath(xpath_expr, namespaces=self.namespaces)

        if not values:
            return default_value
        if multiple:
            return [value.strip() for value in values]
        return values[0].strip()

    def get_data(self):
        title = self.extract_field('//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[@type="main"]/text()', 'Sem título')
        authors = self.get_authors()
        doi = self.extract_field('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:idno[translate(@type, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="doi"]/text()', None)
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

    def get_authors(self):
        authors = []
        author_path = '//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:analytic/tei:author'

        for author in enumerate(self.root.xpath(author_path, namespaces=self.namespaces)):
            first_name = self.extract_field(f'{author_path}/tei:persName/tei:forename[@type="first"]/text()', '')
            middle_name = self.extract_field(f'{author_path}/tei:persName/tei:forename[@type="middle"]/text()', '')
            last_name = self.extract_field(f'{author_path}/tei:persName/tei:surname/text()', '')
            email = self.extract_field(f'{author_path}/tei:email/text()', '')
            
            author_name = " ".join([first_name, middle_name, last_name])
            authors.append({
                'name': author_name,
                'email': email[0] if email else None
            })

        return authors

    def get_sections(self):
        sections = []
        chunk_counter = 1

        section_path = '//tei:text/tei:body/tei:div'

        for section in self.root.xpath(section_path, namespaces=self.namespaces):
            section_title = self.extract_field(f'{section_path}/tei:head/text()', 'Sem título')
            section_text = self.extract_field(f'{section_path}/tei:p/text()', '', True)

            section_text_clean = self.clean_text(section_text)

            for chunk in section_text_clean.split('. '):
                sections.append({
                    'article_id': self.base_filename,
                    'section': section_title,
                    'chunk_id': f'chunk_{chunk_counter}',
                    'text': chunk.strip() + '.',
                    'source_doi': self.extract_field('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:idno[translate(@type, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="doi"]/text()', None)
                })
                chunk_counter += 1

        return sections    

    def clean_text(self, text):
        return " ".join(text).strip().replace("\n", " ").replace("  ", " ")


xml_test = JsonConverter('./data/processed/Appetite and energy balancing (1).grobid.tei.xml')

if __name__ == '__main__':
    xml_test.save_as_json()