import spacy
from main import process_files_in_directory

# Load the spaCy NLP model for text processing
nlp = spacy.load("en_core_web_sm")

if __name__ == '__main__':
    # Defina o diretório onde estão os arquivos processados
    xml_directory = './data/processed'
    
    # Chame a função do main.py passando o diretório e o modelo spaCy
    process_files_in_directory(xml_directory, nlp)