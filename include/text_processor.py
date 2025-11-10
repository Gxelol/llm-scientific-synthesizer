# Define a class for processing text and chunking the text into smaller pieces to make it easier for the language model to process and search efficiently.
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

        # Iterate through sentences and accumulate them into chunks
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
                chunk_text = [sentence] # Start a new chunk
                chunk_size = token_count
            else:
                chunk_text.append(sentence)
                chunk_size += token_count

        # Append the last chunk
        if chunk_text:
            chunks.append({
                "chunk_id": f"chunk_{chunk_id:03}",
                "section": section_title,
                "text": " ".join(chunk_text),
                "source_doi": doi
            })
        
        # Merge small chunks with previous chunk if they contain fewer than 100 words
        if len(chunks) > 1 and len(chunks[-1]["text"].split()) < 100:
            last_chunk = chunks.pop()
            chunks[-1]["text"] += " " + last_chunk["text"]

        return chunks
