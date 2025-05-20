# PDF Knowledge Source Guide

The AMM system now supports PDF files as knowledge sources, allowing you to upload and use PDF documents as part of your agent's knowledge base.

## Overview

PDF support includes:
- Text extraction from both text-based and scanned PDF documents
- Intelligent chunking of PDF content for optimal embedding and retrieval
- Optional OCR (Optical Character Recognition) for scanned documents
- Metadata preservation for each PDF chunk

## Using PDF Knowledge Sources

### In the GUI

1. Navigate to the "Knowledge Sources" section
2. Select the "File" tab
3. Upload a PDF file using the file uploader
4. Enter an ID and optional description
5. Click "Add File Knowledge Source"

The system will automatically detect that your file is a PDF and process it accordingly.

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

## How PDF Processing Works

When a PDF file is added as a knowledge source:

1. The system detects if the PDF is text-based or scanned
2. For text-based PDFs, text is extracted directly
3. For scanned PDFs, OCR is used (if available) to extract text
4. The extracted text is split into chunks of approximately 1000 characters each
5. Each chunk is embedded separately and added to the knowledge base
6. Chunk metadata includes the original filename, PDF type, and chunk position

This chunking approach ensures that even large PDF documents can be processed and retrieved effectively.

## Requirements

To use PDF knowledge sources, the following Python packages are required:
- PyPDF2: For basic PDF parsing
- pdfplumber: For better text extraction with layout preservation

For OCR support with scanned documents, these additional packages are needed:
- pytesseract: Python interface for Tesseract OCR
- pdf2image: Converts PDF pages to images for OCR

These dependencies are included in the main requirements.txt file.

## Troubleshooting

If you encounter issues with PDF processing:

1. **PDF preview not working**: Ensure PyPDF2 and pdfplumber are installed
2. **Poor text extraction**: Try a different PDF format or check encoding
3. **OCR not working**: Verify pytesseract and pdf2image are installed, and Tesseract OCR is available on your system
4. **Memory issues with large PDFs**: Consider splitting the PDF into smaller files before upload

## Limitations

- Very large PDFs may require significant processing time
- Complex formatting (tables, columns) may not be perfectly preserved
- OCR quality depends on the source document's scan quality
- Some PDF security settings may prevent text extraction