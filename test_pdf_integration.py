#!/usr/bin/env python3
"""
PDF Knowledge Integration Test Script

This script verifies that PDF knowledge source integration is working properly.
It creates a sample PDF file, processes it using the PDF processor, and 
attempts to create an AMM with the PDF as a knowledge source.
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime, timezone

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    print("Warning: fpdf not installed. Using text-based test only.")
    print("To install: pip install fpdf")
    HAS_FPDF = False

# Import AMM components
from amm_project.utils.pdf_processor import PDFProcessor, process_pdf
from amm_project.models.amm_models import AMMDesign, KnowledgeSourceType
from amm_project.engine.amm_engine import AMMEngine

def generate_test_pdf(output_path):
    """Generate a simple PDF file for testing."""
    if not HAS_FPDF:
        print("Creating text file instead of PDF...")
        # Create a text file as fallback
        with open(output_path, 'w') as f:
            f.write("This is a test file for the PDF knowledge source integration.\n")
            f.write("It contains some sample text that will be processed by the AMM system.\n")
            f.write("\nThe AMM system should be able to extract this text and use it as a knowledge source.\n")
            f.write("\nThis is just a fallback since FPDF is not installed.\n")
        return

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add some content
    pdf.cell(200, 10, txt="PDF Knowledge Source Test Document", ln=True, align='C')
    pdf.ln(10)
    
    pdf.write(5, "This is a test PDF document for the AMM system. ")
    pdf.write(5, "It contains information about knowledge sources and should be ")
    pdf.write(5, "processed properly by the PDF processor.\n\n")
    
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Knowledge Source Types", ln=True)
    pdf.set_font("Arial", size=12)
    
    pdf.write(5, "The AMM system supports various knowledge source types:\n\n")
    pdf.write(5, "1. Text Files: Plain text files containing information\n")
    pdf.write(5, "2. PDF Documents: PDF files that can be processed and chunked\n")
    pdf.write(5, "3. Direct Text: Text entered directly into the system\n")
    pdf.write(5, "4. Databases: (Coming soon) Structured data sources\n")
    pdf.write(5, "5. Web Content: (Coming soon) Information from websites\n\n")
    
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="PDF Processing Features", ln=True)
    pdf.set_font("Arial", size=12)
    
    pdf.write(5, "The PDF processor supports the following features:\n\n")
    pdf.write(5, "• Text extraction from text-based PDFs\n")
    pdf.write(5, "• OCR for scanned documents (with dependencies)\n")
    pdf.write(5, "• Intelligent chunking for better semantic retrieval\n")
    pdf.write(5, "• Metadata preservation for each chunk\n")
    pdf.write(5, "• Integration with the knowledge source manager\n\n")
    
    # Output the PDF
    pdf.output(output_path)
    print(f"Generated test PDF at: {output_path}")

def test_pdf_processor(pdf_path):
    """Test the PDF processor functionality."""
    print("\n=== Testing PDF Processor ===")
    
    # Create processor
    processor = PDFProcessor()
    
    # Detect PDF type
    pdf_type = processor.detect_pdf_type(pdf_path)
    print(f"Detected PDF type: {pdf_type}")
    
    # Process the PDF
    chunks = processor.process_file(pdf_path)
    
    if not chunks:
        print("Error: No chunks extracted from PDF")
        return False
    
    print(f"Successfully extracted {len(chunks)} chunks from PDF")
    
    # Display sample chunks
    for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
        print(f"\nChunk {i+1}/{len(chunks)} (ID: {chunk['id']})")
        print(f"Length: {len(chunk['text'])} characters")
        print(f"Preview: {chunk['text'][:100]}...")
        print("Metadata:")
        for key, value in chunk['metadata'].items():
            print(f"  {key}: {value}")
    
    return True

def test_amm_integration(pdf_path):
    """Test integrating a PDF as a knowledge source in an AMM."""
    print("\n=== Testing AMM Integration ===")
    
    # Create a simple AMM design
    design = AMMDesign(
        design_id="pdf_test",
        name="PDF Test AMM",
        description="Test AMM with PDF knowledge source",
        knowledge_sources=[
            {
                "id": "pdf_source",
                "name": "Test PDF",
                "type": KnowledgeSourceType.FILE,
                "path": pdf_path,
                "description": "Test PDF document for knowledge retrieval"
            }
        ],
        model_settings={
            "model_type": "gemini-pro",
            "temperature": 0.7
        },
        adaptive_memory={
            "enabled": True
        }
    )
    
    # Create a temporary directory for the AMM
    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize the AMM engine
        try:
            print(f"Initializing AMM engine with base path: {temp_dir}")
            engine = AMMEngine(design, base_data_path=temp_dir)
            print("AMM engine initialized successfully")
            
            # Check if the knowledge source was processed
            if engine.lancedb_table is not None:
                print("LanceDB table initialized")
                print("PDF knowledge source integrated successfully")
                return True
            else:
                print("Warning: LanceDB table not initialized")
                return False
        except Exception as e:
            print(f"Error initializing AMM engine: {type(e).__name__} - {e}")
            return False

def main():
    """Main test function."""
    print("=== PDF Knowledge Source Integration Test ===")
    print(f"Running test at: {datetime.now(timezone.utc).isoformat()}")
    
    # Create a temporary file for the PDF
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    try:
        # Generate test PDF
        generate_test_pdf(pdf_path)
        
        # Test PDF processor
        processor_test_success = test_pdf_processor(pdf_path)
        
        # Test AMM integration
        if processor_test_success:
            amm_test_success = test_amm_integration(pdf_path)
        else:
            print("Skipping AMM integration test due to PDF processor failure")
            amm_test_success = False
        
        # Print summary
        print("\n=== Test Summary ===")
        print(f"PDF Processor Test: {'✓ PASS' if processor_test_success else '✗ FAIL'}")
        print(f"AMM Integration Test: {'✓ PASS' if amm_test_success else '✗ FAIL'}")
        
        if processor_test_success and amm_test_success:
            print("\nSUCCESS: PDF Knowledge Source Integration is working properly!")
            return 0
        else:
            print("\nFAILURE: Some tests did not pass. See above for details.")
            return 1
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(pdf_path)
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())