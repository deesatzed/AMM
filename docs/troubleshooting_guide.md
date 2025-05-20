# AMM System Troubleshooting Guide

This guide documents common errors encountered in the AMM system and their solutions. It serves as a reference for developers to quickly resolve issues based on previous experiences.

## Table of Contents

1. [Import and Module Errors](#import-and-module-errors)
2. [Database and Storage Errors](#database-and-storage-errors)
3. [API and Model Errors](#api-and-model-errors)
4. [Build System Errors](#build-system-errors)
5. [Testing Framework Errors](#testing-framework-errors)
6. [Runtime Errors](#runtime-errors)
7. [Deprecation Warnings](#deprecation-warnings)
8. [PDF Knowledge Source Issues](#pdf-knowledge-source-issues)

## Import and Module Errors

### Error: "module 'datetime' has no attribute 'now'"

**Cause**: Conflicting imports of the datetime module. The file was importing both `from datetime import datetime, timezone` and `import datetime`.

**Solution**: Remove the duplicate import and keep only the specific import:
```python
# Correct
from datetime import datetime, timezone

# Incorrect - remove this
# import datetime
```

**Files Fixed**: `amm_project/engine/amm_engine.py`

### Error: "ImportError: cannot import name 'AMMDesign' from..."

**Cause**: Incorrect import path for AMMDesign class.

**Solution**: Update the import statement to use the correct path:
```python
# Correct
from amm_project.models.amm_models import AMMDesign

# Incorrect
# from amm_models import AMMDesign
```

**Files Fixed**: `news_agent_simulator.py`, `amm_gui/utils/amm_integration.py`

## Database and Storage Errors

### Error: "sqlite3.OperationalError: unable to open database file"

**Cause**: The `mock_path_mkdir` fixture in tests was preventing the actual creation of the directory needed by SQLite.

**Solution**: Remove `mock_path_mkdir` from the test's arguments to allow the engine's `_initialize_paths` method to create the directory using the real `Path.mkdir`.

**Files Fixed**: Test fixtures in `tests/unit/test_amm_engine.py`

### Error: "LanceDB connection failed"

**Cause**: Missing or incorrect LanceDB path, or the directory doesn't exist.

**Solution**: Ensure the LanceDB path exists and has proper permissions:
```python
# Ensure directory exists before connecting
lancedb_path = Path(self.lancedb_path)
lancedb_path.mkdir(parents=True, exist_ok=True)
self.lancedb_connection = lancedb.connect(str(lancedb_path))
```

## API and Model Errors

### Error: "AttributeError: 'AMMDesign' object has no attribute 'prompts'"

**Cause**: The attribute structure changed from `design.prompts.system_instruction` to `design.agent_prompts.system_instruction`.

**Solution**: Update references to use the new attribute path:
```python
# Correct
system_prompt = self.design.agent_prompts.system_instruction

# Incorrect
# system_prompt = self.design.prompts.system_instruction
```

**Files Fixed**: `amm_project/engine/amm_engine.py`

### Error: "AttributeError: 'InteractionRecordPydantic' object has no attribute 'timestamp_utc'"

**Cause**: Field name mismatch between the code and the Pydantic model.

**Solution**: Update the code to use the correct field name:
```python
# Correct
record_data.timestamp

# Incorrect
# record_data.timestamp_utc
```

**Files Fixed**: `AMMEngine.add_interaction_record` in `amm_project/engine/amm_engine.py`

## Build System Errors

### Error: "TypeError: build_amm() missing 1 required positional argument: 'requirements_path'"

**Cause**: Missing required argument when calling the build_amm function.

**Solution**: Provide all required arguments:
```python
# Correct
build_dir = build_amm(str(temp_design_path), "builds", "requirements.txt")

# Incorrect
# build_dir = build_amm(str(temp_design_path), "builds")
```

**Files Fixed**: `amm_gui/app.py`

## Testing Framework Errors

### Error: "fixture 'mock_method' not found"

**Cause**: Incorrect parameter names or order when using `@patch` decorators from `pytest-mock`.

**Solution**: Follow these rules for mock parameters:
1. The parameter name must exactly match the last component of the patched path
2. All mock-injected parameters must appear first in the test function's signature
3. The order of mock parameters must match the order of the `@patch` decorators when read from bottom-up

```python
# Correct
@patch('module.Class.method')
def test_function(method, other_fixture):
    # Test code

# Incorrect
@patch('module.Class.method')
def test_function(other_fixture, wrong_name):
    # Test code
```

**Files Fixed**: `tests/unit/test_amm_engine.py`

### Error: "AssertionError: Expected log message not found"

**Cause**: Test expecting 'IOError' in log message but actual log showed 'OSError'.

**Solution**: Update the expected log message to match the actual exception type:
```python
# Correct - OSError is used in Python 3 (IOError is an alias)
mock_read_text.side_effect = OSError("Test error")
assert "OSError" in caplog.text

# Incorrect
# mock_read_text.side_effect = IOError("Test error")
# assert "IOError" in caplog.text
```

**Files Fixed**: `test_initialize_knowledge_sources_file_read_error` in `tests/unit/test_amm_engine.py`

## Runtime Errors

### Error: "NameError: name 'desc' is not defined"

**Cause**: Missing import for SQLAlchemy's `desc` function.

**Solution**: Add the required import:
```python
from sqlalchemy import desc
```

**Files Fixed**: `AMMEngine.get_recent_interaction_records` in `amm_project/engine/amm_engine.py`

### Error: "KeyError: 'model_name' when calling Gemini API"

**Cause**: Missing or incorrect environment variables for model configuration.

**Solution**: Ensure environment variables are properly set and loaded:
```python
# Add fallback values for environment variables
model_name = os.getenv("MODEL", "gemini-1.5-flash")
```

## Deprecation Warnings

### Warning: "DeprecationWarning: Pydantic V1 style `@validator` is deprecated"

**Cause**: Using deprecated Pydantic V1 validator decorators.

**Solution**: Update to Pydantic V2 field validators:
```python
# Pydantic V2
from pydantic import field_validator

class MyModel(BaseModel):
    name: str
    
    @field_validator('name')
    def validate_name(cls, v):
        if not v:
            raise ValueError("Name cannot be empty")
        return v

# Deprecated Pydantic V1
# from pydantic import validator
# 
# class MyModel(BaseModel):
#     name: str
#     
#     @validator('name')
#     def validate_name(cls, v):
#         if not v:
#             raise ValueError("Name cannot be empty")
#         return v
```

### Warning: "DeprecationWarning: The 'orm_mode' is deprecated"

**Cause**: Using deprecated `orm_mode` configuration in Pydantic models.

**Solution**: Replace with `model_config` using `ConfigDict`:
```python
# Pydantic V2
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

# Deprecated Pydantic V1
# class MyModel(BaseModel):
#     class Config:
#         orm_mode = True
```

**Files Fixed**: Pydantic models in `amm_project/models/memory_models.py`

### Warning: "DeprecationWarning: datetime.datetime.utcnow() is deprecated"

**Cause**: Using deprecated `datetime.datetime.utcnow()` method.

**Solution**: Replace with timezone-aware `datetime.datetime.now(datetime.timezone.utc)`:
```python
# Correct
from datetime import datetime, timezone
timestamp = datetime.now(timezone.utc)

# Deprecated
# import datetime
# timestamp = datetime.datetime.utcnow()
```

**Files Fixed**: `amm_project/models/memory_models.py` and `amm_project/engine/amm_engine.py`

### Warning: "DeprecationWarning: from_orm is deprecated"

**Cause**: Using deprecated `from_orm` method in Pydantic models.

**Solution**: Replace with `model_validate`:
```python
# Pydantic V2
pydantic_model = MyModel.model_validate(orm_instance)

# Deprecated Pydantic V1
# pydantic_model = MyModel.from_orm(orm_instance)
```

**Files Fixed**: `amm_project/engine/amm_engine.py`

## General Troubleshooting Steps

1. **Check Logs**: Always check the application logs first for error details
2. **Verify Environment**: Ensure all environment variables are correctly set
3. **Check Permissions**: Verify file and directory permissions for database and knowledge files
4. **Validate Inputs**: Ensure all inputs match the expected schema
5. **Test in Isolation**: Test components in isolation to identify the source of the issue
6. **Check Dependencies**: Verify all dependencies are installed with the correct versions

## Adding to This Guide

When fixing a new error:

1. Document the error message and type
2. Explain the root cause
3. Provide the solution with code examples
4. Note which files were fixed
5. Add to the appropriate section of this guide

This approach ensures knowledge is preserved and helps prevent the same errors from recurring.

## PDF Knowledge Source Issues

### Error: "ImportError: No module named 'PyPDF2'"

**Cause**: The PDF processor requires PyPDF2 but it is not installed.

**Solution**: Install the PDF processing dependencies:
```bash
pip install PyPDF2>=3.0.0 pdfplumber>=0.10.1
```

**Files Affected**: `amm_project/utils/pdf_processor.py`

### Error: "PDF content extraction failed" or "No text extracted from PDF"

**Cause**: The PDF might be scanned or image-based without OCR capabilities.

**Solution**: Install OCR dependencies and ensure Tesseract is available:
```bash
# Install Python libraries
pip install pytesseract>=0.3.10 pdf2image>=1.16.3

# Install Tesseract OCR (OS-specific)
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
# macOS
brew install tesseract
# Windows: Download the installer from https://github.com/UB-Mannheim/tesseract/wiki
```

**Note**: Verify your Tesseract installation with:
```bash
tesseract --version
```

### Error: "OSError: Unable to locate poppler"

**Cause**: The pdf2image library requires poppler-utils to be installed.

**Solution**: Install poppler-utils:
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils
# macOS
brew install poppler
# Windows: Download and extract poppler from http://blog.alivate.com.au/poppler-windows/
```

### Error: "AttributeError: 'property' object has no attribute 'return_value'" in tests

**Cause**: Incorrectly patching properties in unit tests.

**Solution**: Use the `new_callable` parameter with `PropertyMock`:
```python
from unittest.mock import PropertyMock

# Correct way to mock a property
with patch('pathlib.Path.suffix', new_callable=PropertyMock) as mock_suffix:
    mock_suffix.return_value = '.pdf'
    # Test code
```

### Error: "Cannot read image as bytes" during OCR processing

**Cause**: Issues with the pdf2image conversion during OCR.

**Solution**: Ensure you have both poppler-utils and Tesseract properly installed, and check the PDF file:
```python
# Check if a PDF page can be converted to an image
from pdf2image import convert_from_path
try:
    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    if images:
        print("PDF to image conversion successful")
except Exception as e:
    print(f"PDF to image conversion failed: {e}")
```

### Error: "PDF chunks have poor semantic relevance"

**Cause**: Default chunking parameters may not be optimal for certain documents.

**Solution**: Adjust chunking parameters based on document content:
```python
# For documents with longer, cohesive sections:
processor = PDFProcessor({
    "chunk_size": 1500,      # Larger chunks for more context
    "chunk_overlap": 300,    # More overlap to maintain context
    "min_chunk_size": 100    # Higher minimum to avoid tiny chunks
})

# For technical documents with dense information:
processor = PDFProcessor({
    "chunk_size": 800,       # Smaller chunks for focused information
    "chunk_overlap": 200,    # Standard overlap
    "min_chunk_size": 50     # Lower minimum to capture small but important sections
})
```

**Files Affected**: Custom implementation code using `PDFProcessor`
