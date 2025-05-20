#!/usr/bin/env python3
"""
PDF Knowledge Source Demo

This script demonstrates how to use the PDF processor to extract and chunk text
from a PDF file, and how to use it with AMM.

Usage:
  python pdf_knowledge_demo.py <path_to_pdf_file>
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from amm_project.utils.pdf_processor import PDFProcessor, process_pdf
except ImportError:
    print("Error: PDF processor module not found. Make sure you're running from the correct directory.")
    sys.exit(1)

def demo_pdf_processing(pdf_path):
    """Demonstrate PDF processing capabilities."""
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)
        
    print(f"\n{'=' * 60}")
    print(f"PDF KNOWLEDGE SOURCE DEMO")
    print(f"{'=' * 60}")
    print(f"Processing PDF: {pdf_path}")
    
    # Initialize the processor
    processor = PDFProcessor(config={
        "chunk_size": 500,  # Smaller chunks for the demo
        "chunk_overlap": 100,
        "min_chunk_size": 20
    })
    
    # Detect PDF type
    pdf_type = processor.detect_pdf_type(pdf_path)
    print(f"\nPDF Type: {pdf_type}")
    
    # Process the PDF file
    print("\nProcessing PDF into chunks...")
    chunks = processor.process_file(pdf_path)
    
    # Display results
    if not chunks:
        print("No text could be extracted from the PDF.")
        return
        
    print(f"\nSuccessfully extracted {len(chunks)} chunks from the PDF.")
    
    # Show a sample of the chunks
    max_samples = min(3, len(chunks))
    for i in range(max_samples):
        chunk = chunks[i]
        print(f"\n--- Chunk {i+1}/{max_samples} (ID: {chunk['id']}) ---")
        print(f"Length: {len(chunk['text'])} characters")
        print(f"Preview: {chunk['text'][:100]}...")
        print("\nMetadata:")
        for key, value in chunk['metadata'].items():
            print(f"  {key}: {value}")
    
    # Show how to integrate with AMM
    print(f"\n{'=' * 60}")
    print("INTEGRATION WITH AMM")
    print(f"{'=' * 60}")
    
    print("\nSample AMM design JSON with this PDF as a knowledge source:")
    
    design = {
        "design_id": "pdf_demo",
        "name": "PDF Knowledge Demo",
        "description": "AMM with PDF knowledge source",
        "model_settings": {
            "model_type": "gemini-pro",
            "temperature": 0.7
        },
        "knowledge_sources": [
            {
                "id": "pdf_knowledge",
                "name": "PDF Document",
                "type": "file",
                "path": pdf_path,
                "description": "PDF document for knowledge retrieval"
            }
        ],
        "adaptive_memory": {
            "enabled": True,
            "memory_window": 10
        }
    }
    
    print(json.dumps(design, indent=2))
    
    print("\nWhen using this design, the AMM engine will:")
    print("1. Detect that the knowledge source is a PDF file")
    print("2. Process the PDF into chunks using the PDF processor")
    print("3. Generate embeddings for each chunk")
    print("4. Store the chunks in the vector database")
    print("5. Retrieve relevant chunks when processing queries")
    
    print(f"\n{'=' * 60}")
    print("DIRECT USAGE EXAMPLE")
    print(f"{'=' * 60}")
    
    print("""
# Python code to directly use the PDF processor:

from amm_project.utils.pdf_processor import process_pdf

# Process a PDF file
chunks = process_pdf("path/to/document.pdf")

# Use the extracted text
for chunk in chunks:
    print(f"Chunk ID: {chunk['id']}")
    print(f"Text: {chunk['text'][:100]}...")
    print(f"PDF Type: {chunk['metadata']['pdf_type']}")
    
# To customize chunking:
chunks = process_pdf(
    "path/to/document.pdf",
    chunk_size=1000,
    chunk_overlap=200,
    min_chunk_size=50
)
""")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path_to_pdf_file>")
        sys.exit(1)
        
    pdf_path = sys.argv[1]
    demo_pdf_processing(pdf_path)