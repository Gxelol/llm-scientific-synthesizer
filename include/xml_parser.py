from lxml import etree

# Define a class for parsing XML files and extracting information
class XmlParser:
    def __init__(self, file_path):
        # Parse the XML file and get its root element
        self.tree = etree.parse(file_path)
        self.root = self.tree.getroot()
        self.namespaces = {'tei': 'http://www.tei-c.org/ns/1.0'} # TEI XML namespace
    
    def get_title(self):
        # Extract the title of the document
        return self.root.xpath('//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title[@type="main"]/text()', namespaces=self.namespaces)

    def get_doi(self):
        # Extract the DOI (Digital Object Identifier)
        return self.root.xpath('//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:biblStruct/tei:idno[translate(@type, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")="doi"]/text()', namespaces=self.namespaces)

    def get_authors(self):
        # Extract author details 
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
        # Extract section title and texts
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