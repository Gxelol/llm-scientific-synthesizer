import json
import pandas as pd

from lxml import etree

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

            sections.append({
                'title': title,
                'text': text
            })

        return sections    

    def clean_text(self, text):
        return " ".join(text).strip().replace("\n", " ").replace("  ", " ")


xml_test = JsonConverter('./data/processed/Appetite and energy balancing (1).grobid.tei.xml')

if __name__ == '__main__':
    xml_test.save_as_json()