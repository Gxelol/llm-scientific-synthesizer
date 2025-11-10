import os

from include.json_converter import JsonConverter

def process_files_in_directory(directory_path, nlp):
    # Process XML files in the specified directory
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

