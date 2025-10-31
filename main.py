import json
import pandas as pd

from lxml import etree

class JsonConverter():
    def __init__(self, file_path):
        self.namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'}
        self.tree = etree.parse(file_path)
        self.root = self.tree.getroot()
    

    def get_data(self):
        title = self.get_title()
        authors = self.get_authors()
        doi = self.get_doi()
        sections = self.get_sections()

        print(title, doi, authors, sections)

    def get_authors(self):
        authors = []

        for author in self.root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:analytic/tei:author', namespaces=self.namespaces):
            first_name = author.xpath('tei:persName/tei:forename[@type="first"]/text()', namespaces=self.namespaces)
            middle_name = author.xpath('tei:persName/tei:forename[@type="middle"]/text()', namespaces=self.namespaces)
            last_name = author.xpath('tei:persName/tei:surname/text()', namespaces=self.namespaces)
            email = author.xpath('tei:email/text()', namespaces=self.namespaces)
                
            author_name = " ".join(first_name + middle_name + last_name)
            authors.append({
                'name': author_name,
                'email': email[0] if email else None
            })

        return authors

    def get_title(self):
        return self.root.xpath('//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[@type="main"]/text()', namespaces=self.namespaces)

    def get_doi(self):
        return self.root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:idno[translate(@type, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="doi"]/text()', namespaces=self.namespaces)

    def get_sections(self):
        sections = []

        for section in self.root.xpath('//tei:text/tei:body/tei:div', namespaces=self.namespaces):
            section_title = section.xpath('tei:head/text()', namespaces=self.namespaces)
            section_text = section.xpath('tei:p/text()', namespaces=self.namespaces)

            sections.append({
                'section_title': section_title[0] if section_title else "Sem título",
                'section_text': " ".join(section_text) if section_text else ""
            })

        return sections    

xml_test = JsonConverter('./data/processed/Appetite and energy balancing (1).grobid.tei.xml')

if __name__ == '__main__':
    xml_test.get_data()