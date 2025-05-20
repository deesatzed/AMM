#!/usr/bin/env python3
"""
PDF Knowledge Source Web Demo

A simple Flask web application that demonstrates how to use the PDF processor
to extract and chunk text from uploaded PDF files.

Usage:
  python pdf_web_demo.py
  
Requirements:
  flask
  werkzeug
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from flask import Flask, request, render_template_string, redirect, url_for
    from werkzeug.utils import secure_filename
except ImportError:
    print("Error: Flask or Werkzeug not found. Install with: pip install flask werkzeug")
    sys.exit(1)

try:
    from amm_project.utils.pdf_processor import PDFProcessor
except ImportError:
    print("Error: PDF processor module not found. Make sure you're running from the correct directory.")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
app.config['SECRET_KEY'] = 'pdf-knowledge-demo'

# Initialize PDF processor
pdf_processor = PDFProcessor()

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PDF Knowledge Source Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        h1, h2, h3 {
            color: #333;
        }
        .container {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: #f9f9f9;
        }
        .chunk {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 15px;
            background-color: white;
        }
        .metadata {
            font-size: 0.9em;
            color: #555;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px dashed #ddd;
        }
        .preview {
            height: 150px;
            overflow-y: auto;
            font-size: 0.9em;
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
        }
        .options {
            margin-top: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="number"] {
            width: 80px;
            margin-right: 10px;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #777;
        }
    </style>
</head>
<body>
    <h1>PDF Knowledge Source Demo</h1>
    
    <div class="container">
        <h2>Upload a PDF</h2>
        <form method="post" enctype="multipart/form-data">
            <div>
                <label for="pdf_file">PDF File:</label>
                <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required>
            </div>
            
            <div class="options">
                <h3>Processing Options</h3>
                <div>
                    <label for="chunk_size">Chunk Size (characters):</label>
                    <input type="number" id="chunk_size" name="chunk_size" value="500" min="100" max="5000">
                </div>
                <div>
                    <label for="chunk_overlap">Chunk Overlap:</label>
                    <input type="number" id="chunk_overlap" name="chunk_overlap" value="100" min="0" max="1000">
                </div>
                <div>
                    <label for="min_chunk_size">Min Chunk Size:</label>
                    <input type="number" id="min_chunk_size" name="min_chunk_size" value="20" min="1" max="500">
                </div>
            </div>
            
            <div style="margin-top: 20px;">
                <button type="submit">Process PDF</button>
            </div>
        </form>
    </div>
    
    {% if results %}
    <div class="container">
        <h2>Processing Results</h2>
        <p><strong>PDF Type:</strong> {{ results.pdf_type }}</p>
        <p><strong>Total Chunks:</strong> {{ results.chunks|length }}</p>
        
        <h3>Extracted Chunks:</h3>
        {% for chunk in results.chunks %}
        <div class="chunk">
            <h4>Chunk {{ loop.index }}/{{ results.chunks|length }} (ID: {{ chunk.id }})</h4>
            <div class="preview">{{ chunk.text }}</div>
            <div class="metadata">
                <strong>Metadata:</strong><br>
                {% for key, value in chunk.metadata.items() %}
                {{ key }}: {{ value }}<br>
                {% endfor %}
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <div class="footer">
        AMM PDF Knowledge Source Extension Demo
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'pdf_file' not in request.files:
            return render_template_string(HTML_TEMPLATE, results=None)
            
        file = request.files['pdf_file']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, results=None)
            
        if file and file.filename.lower().endswith('.pdf'):
            # Get processing options
            chunk_size = int(request.form.get('chunk_size', 500))
            chunk_overlap = int(request.form.get('chunk_overlap', 100))
            min_chunk_size = int(request.form.get('min_chunk_size', 20))
            
            # Save the file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Initialize processor with custom config
            processor = PDFProcessor({
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "min_chunk_size": min_chunk_size
            })
            
            # Process the PDF
            pdf_type = processor.detect_pdf_type(filepath)
            chunks = processor.process_file(filepath)
            
            # Prepare results
            results = {
                "pdf_type": pdf_type,
                "chunks": chunks
            }
            
            # Clean up the file
            try:
                os.remove(filepath)
            except:
                pass
    
    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == '__main__':
    print("\nPDF Knowledge Source Web Demo")
    print("=============================")
    print("Navigate to http://127.0.0.1:5000 in your browser")
    print("Upload a PDF file to see it processed into knowledge chunks")
    print("Press Ctrl+C to exit\n")
    
    # Create a README for the examples directory
    readme_path = Path(__file__).parent / "README.md"
    if not readme_path.exists():
        with open(readme_path, "w") as f:
            f.write("""# PDF Knowledge Source Examples

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
""")
    
    app.run(debug=True)