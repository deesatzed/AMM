# GitHub Integration Guide

This guide provides instructions for integrating the PDF Knowledge Source Extension with your existing AMM GitHub repository.

## Option 1: Manual Integration

This approach is best if you have customized your AMM codebase significantly.

1. Fork your existing AMM repository on GitHub

2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/your-amm-repo.git
   cd your-amm-repo
   ```

3. Create a new branch for the PDF integration:
   ```bash
   git checkout -b feature/pdf-knowledge-support
   ```

4. Copy files from this package to your repository, maintaining the same directory structure:
   ```bash
   # Example: copying the PDF processor
   cp /path/to/package/amm_project/utils/pdf_processor.py ./amm_project/utils/
   
   # Copy all files maintaining directory structure
   # ...
   ```

5. Update requirements.txt with the new dependencies:
   ```bash
   # Add to your existing requirements.txt
   PyPDF2>=3.0.0
   pdfplumber>=0.10.1
   pytesseract>=0.3.10  # Optional - for OCR
   pdf2image>=1.16.3    # Optional - for OCR
   ```

6. Test the integration:
   ```bash
   # Run the PDF processor tests
   python -m unittest tests/unit/test_pdf_processor.py
   
   # Run the file handling tests
   python -m unittest tests/unit/test_file_handling.py
   ```

7. Commit your changes:
   ```bash
   git add .
   git commit -m "Add PDF knowledge source support"
   ```

8. Push to GitHub and create a pull request:
   ```bash
   git push origin feature/pdf-knowledge-support
   ```

9. On GitHub, create a pull request from your `feature/pdf-knowledge-support` branch to your main branch

## Option 2: Using Git Subtree (Advanced)

This approach allows you to maintain the PDF extension as a separate component while integrating it with your main repository.

1. Add this repository as a remote in your main AMM repository:
   ```bash
   git remote add pdf-extension https://github.com/username/amm-pdf-extension.git
   git fetch pdf-extension
   ```

2. Add the PDF extension as a subtree in your repository:
   ```bash
   git subtree add --prefix=extensions/pdf-extension pdf-extension main --squash
   ```

3. Update your code to import from the extensions directory:
   ```python
   try:
       from extensions.pdf-extension.amm_project.utils.pdf_processor import PDFProcessor
       PDF_PROCESSOR_AVAILABLE = True
   except ImportError:
       print("PDF processor not available. PDF knowledge sources will be skipped.")
       PDF_PROCESSOR_AVAILABLE = False
   ```

4. When you need to update the extension:
   ```bash
   git subtree pull --prefix=extensions/pdf-extension pdf-extension main --squash
   ```

## Option 3: Using as a Plugin (If AMM Supports Plugins)

If your AMM version supports a plugin architecture:

1. Package this as a plugin:
   ```bash
   # Create a plugins directory if it doesn't exist
   mkdir -p your-amm-repo/plugins/pdf-extension
   
   # Copy the files into the plugin directory
   cp -r /path/to/package/* your-amm-repo/plugins/pdf-extension/
   ```

2. Follow your AMM's plugin registration mechanism to enable the extension

## After Integration

Regardless of which method you choose:

1. Update your documentation to mention PDF support
2. Add the PDF Knowledge Guide to your docs directory
3. Update your README.md to list PDF support as a feature
4. Consider creating a demo or tutorial showing PDF knowledge source usage