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
