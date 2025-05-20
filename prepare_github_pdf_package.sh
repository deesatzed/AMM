#!/bin/bash
# Script to prepare a GitHub package with PDF knowledge source support

set -e

# Set source and target directories
SOURCE_DIR="."
TARGET_DIR="./github_package"
DATE_TAG=$(date +"%Y-%m-%d")

echo "Preparing GitHub package with PDF knowledge source support..."

# Create target directory structure
mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/amm_project/utils"
mkdir -p "$TARGET_DIR/amm_gui/utils"
mkdir -p "$TARGET_DIR/amm_gui/components"
mkdir -p "$TARGET_DIR/docs"
mkdir -p "$TARGET_DIR/tests/unit"

# Copy core PDF processor component
cp "$SOURCE_DIR/amm_project/utils/pdf_processor.py" "$TARGET_DIR/amm_project/utils/"
cp "$SOURCE_DIR/amm_project/utils/__init__.py" "$TARGET_DIR/amm_project/utils/"

# Copy updated GUI components
cp "$SOURCE_DIR/amm_gui/utils/file_handling.py" "$TARGET_DIR/amm_gui/utils/"
cp "$SOURCE_DIR/amm_gui/utils/__init__.py" "$TARGET_DIR/amm_gui/utils/"
cp "$SOURCE_DIR/amm_gui/components/knowledge_source_manager.py" "$TARGET_DIR/amm_gui/components/"
cp "$SOURCE_DIR/amm_gui/components/__init__.py" "$TARGET_DIR/amm_gui/components/"

# Copy documentation
cp "$SOURCE_DIR/docs/pdf_knowledge_guide.md" "$TARGET_DIR/docs/"

# Copy tests
cp "$SOURCE_DIR/tests/unit/test_pdf_processor.py" "$TARGET_DIR/tests/unit/"
cp "$SOURCE_DIR/tests/unit/test_file_handling.py" "$TARGET_DIR/tests/unit/"
cp "$SOURCE_DIR/tests/unit/__init__.py" "$TARGET_DIR/tests/unit/"
mkdir -p "$TARGET_DIR/tests/__init__.py"
touch "$TARGET_DIR/tests/__init__.py"

# Copy requirements.txt with PDF dependencies
cp "$SOURCE_DIR/requirements.txt" "$TARGET_DIR/"

# Create README
cat > "$TARGET_DIR/README.md" << 'EOL'
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
EOL

# Add installation instructions
cat > "$TARGET_DIR/INSTALL.md" << 'EOL'
# Installation Guide

Follow these steps to install the PDF knowledge source extension in your AMM project:

## 1. Install Dependencies

```bash
# Install core dependencies
pip install PyPDF2>=3.0.0 pdfplumber>=0.10.1

# Optional: Install OCR dependencies (for scanned documents)
pip install pytesseract>=0.3.10 pdf2image>=1.16.3

# Note: OCR will also require Tesseract to be installed on your system
# For Ubuntu/Debian: sudo apt-get install tesseract-ocr
# For macOS: brew install tesseract
# For Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki
```

## 2. Copy Files to Your Project

1. Copy `amm_project/utils/pdf_processor.py` to your project's utils directory
2. Copy `amm_gui/utils/file_handling.py` to your project's GUI utils directory 
3. Copy `amm_gui/components/knowledge_source_manager.py` to your GUI components directory
4. Copy `docs/pdf_knowledge_guide.md` to your project's docs directory

## 3. Update Engine (if needed)

If you've customized your AMM engine, you may need to manually integrate the PDF processing code:

1. Import PDF processor in your engine:
   ```python
   try:
       from amm_project.utils.pdf_processor import PDFProcessor
       PDF_PROCESSOR_AVAILABLE = True
   except ImportError:
       print("PDF processor not available. PDF knowledge sources will be skipped.")
       PDF_PROCESSOR_AVAILABLE = False
   ```

2. Add PDF handling to your file knowledge source processing code in the engine

## 4. Test the Installation

Run the included unit tests to verify the installation:

```bash
python -m unittest tests/unit/test_pdf_processor.py
python -m unittest tests/unit/test_file_handling.py
```

## 5. Try it Out

1. Launch the AMM GUI
2. Go to the Knowledge Sources section
3. Upload a PDF file
4. Check that it's processed correctly
EOL

# Create a changelog
cat > "$TARGET_DIR/CHANGELOG.md" << EOL
# Changelog

## PDF Knowledge Source Extension - $DATE_TAG

### Added
- PDF processor utility for extracting and chunking text from PDF files
- Support for both text-based and scanned PDFs
- Optional OCR capabilities for scanned documents
- PDF knowledge source integration in the AMM GUI
- Preview support for PDF files in the knowledge source manager
- Comprehensive documentation in PDF knowledge guide
- Unit tests for PDF processor and file handling

### Modified
- Updated file handling utilities to support PDF files
- Enhanced knowledge source manager with PDF information
- Added PDF processing dependencies to requirements.txt
EOL

# Create a ZIP file
cd "$SOURCE_DIR"
zip -r "amm_pdf_extension_$DATE_TAG.zip" "$TARGET_DIR"

echo "Package prepared successfully at: $TARGET_DIR"
echo "ZIP file created: amm_pdf_extension_$DATE_TAG.zip"