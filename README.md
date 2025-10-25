# LLM Scientific Synthesizer

## Project Description
**LLM Scientific Synthesizer** is an experimental application designed to **extract, summarize, and synthesize scientific evidence** from a closed corpus of peer-reviewed papers.

The project implements a **Retrieval-Augmented Generation (RAG)** pipeline that combines automatic extraction of academic PDFs with LLM-based summarization.  
Each generated summary is **traceable to the original text segments**, ensuring transparency, verifiability, and minimal hallucination risk.

The final goal is to enable the creation of **automated scientific reports or eBooks** built exclusively from verified sources — *no external web data access*.

---

## Overall Architecture

```text
Scientific PDFs → Extraction (GROBID)
→ Cleaning & Chunking → Embeddings & Vector Index (FAISS/Chroma)
→ Query + Generation (RAG + LLM)
→ Human-in-the-loop Review Interface
→ Export (Markdown/PDF)

