# PDF Knowledge Source Examples

This directory contains examples demonstrating how to use the PDF knowledge source extension.

## Examples:

1. **pdf_knowledge_demo.py** - Command-line demo showing how to process a PDF file
   ```bash
   python pdf_knowledge_demo.py path/to/your.pdf
   ```

2. **pdf_web_demo.py** - Web-based demo with a simple Flask interface
   ```bash
   pip install flask werkzeug
   python pdf_web_demo.py
   ```
   Then navigate to http://127.0.0.1:5000 in your browser.

## Example Files

The `examples_data` directory contains sample PDF files you can use to test the PDF processor:

- Place PDF files in this directory to use with the demo scripts
- Both text-based and scanned PDFs can be tested
- Smaller PDF files (1-5 pages) work best for quick demonstrations

## What to Look For

When running the examples, pay attention to:

1. **PDF Type Detection** - The processor will detect if your PDF is text-based or scanned
2. **Chunking Strategy** - Notice how the processor breaks the PDF into manageable chunks
3. **Metadata Preservation** - Each chunk retains information about its source and position
4. **OCR Support** - If your system has OCR libraries installed, scanned PDFs will be processed with OCR

## Integration Tips

- Use the `process_pdf()` function for simple one-time processing
- Use the `PDFProcessor` class for more control over chunking parameters
- When working with the AMM system, just use `.pdf` files as knowledge sources, and the system will handle them automatically
- For large PDFs, you may need to adjust the chunking parameters