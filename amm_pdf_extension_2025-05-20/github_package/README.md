# AMM PDF Knowledge Source Extension

This package adds PDF knowledge source support to the Agno Memory Module (AMM) system. It enables the system to process, chunk, and embed PDF documents for use as knowledge sources.

## Features

- Text extraction from both text-based and scanned PDF documents
- Intelligent chunking of PDF content for optimal embedding and retrieval
- Optional OCR (Optical Character Recognition) for scanned documents
- Metadata preservation for each PDF chunk
- Integration with the AMM GUI knowledge source manager
- Preview support for PDF files in the GUI

## Installation

1. Copy the files to your AMM project
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### In the GUI

1. Navigate to the "Knowledge Sources" section
2. Select the "File" tab
3. Upload a PDF file using the file uploader
4. Enter an ID and optional description
5. Click "Add File Knowledge Source"

### In Design Files

You can also include PDF files in your AMM design JSON:

```json
{
  "knowledge_sources": [
    {
      "id": "product_manual",
      "name": "Product Manual",
      "type": "file",
      "path": "/path/to/manual.pdf",
      "description": "Product manual for our latest device"
    }
  ]
}
```

## Documentation

For more information, see [PDF Knowledge Guide](docs/pdf_knowledge_guide.md).

## Requirements

- PyPDF2: For basic PDF parsing
- pdfplumber: For better text extraction with layout preservation
- pytesseract (optional): Python interface for Tesseract OCR
- pdf2image (optional): Converts PDF pages to images for OCR
