"""
Tests for the PDF processor module.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Try importing the module directly - this will fail if dependencies aren't installed
try:
    from amm_project.utils.pdf_processor import PDFProcessor, process_pdf
    PDF_PROCESSOR_AVAILABLE = True
except ImportError:
    PDF_PROCESSOR_AVAILABLE = False


@unittest.skipIf(not PDF_PROCESSOR_AVAILABLE, "PDF processor dependencies not available")
class TestPDFProcessor(unittest.TestCase):
    """Test cases for the PDF processor module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Override imports check with mocks
        self.patch_pypdf = patch('amm_project.utils.pdf_processor.PDFProcessor.PyPDF2', create=True)
        self.mock_pypdf = self.patch_pypdf.start()
        
        # Set up PDF reader mock
        self.mock_pdf_reader = MagicMock()
        self.mock_page = MagicMock()
        self.mock_page.extract_text.return_value = "This is test content from a PDF page."
        self.mock_pdf_reader.pages = [self.mock_page, self.mock_page]
        self.mock_pypdf.PdfReader.return_value = self.mock_pdf_reader
        
        # Create processor instance with mocked components
        self.processor = PDFProcessor()
        self.processor.PyPDF2 = self.mock_pypdf
        
        # Patch os.path.exists for fake files
        self.patch_exists = patch('os.path.exists')
        self.mock_exists = self.patch_exists.start()
        self.mock_exists.return_value = True
        
        # Patch file opening functions
        self.patch_open = patch('builtins.open', create=True)
        self.mock_open = self.patch_open.start()
        
        # Sample config
        self.test_config = {
            "chunk_size": 500,
            "chunk_overlap": 100,
            "min_chunk_size": 20
        }
    
    def tearDown(self):
        """Clean up after tests."""
        self.patch_pypdf.stop()
        self.patch_exists.stop()
        self.patch_open.stop()
    
    def test_initialization(self):
        """Test processor initialization with config."""
        processor = PDFProcessor(self.test_config)
        self.assertEqual(processor.chunk_size, 500)
        self.assertEqual(processor.chunk_overlap, 100)
        self.assertEqual(processor.min_chunk_size, 20)
    
    def test_detect_pdf_type(self):
        """Test PDF type detection."""
        # Skip this test until we have better mocks
        self.skipTest("Needs better PDF mocking")
    
    def test_extract_text(self):
        """Test text extraction."""
        # Skip this test until we have better mocks
        self.skipTest("Needs better PDF mocking")
    
    def test_chunk_text(self):
        """Test text chunking functionality."""
        test_text = "This is a test paragraph. It contains multiple sentences. " * 10
        chunks = self.processor._chunk_text(test_text)
        # Should create chunks of appropriate size
        self.assertTrue(len(chunks) > 0)
        self.assertTrue(all(len(chunk) <= self.processor.chunk_size for chunk in chunks))
    
    @patch('uuid.uuid4')
    def test_process_file_mocked(self, mock_uuid):
        """Test complete file processing with mocked PDF processing."""
        # Skip real file processing and test the chunking directly
        mock_uuid.hex = "12345678"
        
        # Create mock text directly
        with patch.object(PDFProcessor, '_extract_text') as mock_extract:
            mock_extract.return_value = "Test content for chunking. " * 30
            
            with patch.object(PDFProcessor, 'detect_pdf_type') as mock_detect:
                mock_detect.return_value = "text"
                
                chunks = self.processor.process_file("fake_path.pdf")
                
                # Verify chunking behavior
                self.assertTrue(len(chunks) > 0)
                # Check structure of first chunk
                self.assertIn("id", chunks[0])
                self.assertIn("text", chunks[0])
                self.assertEqual(chunks[0]["source_type"], "pdf")
                self.assertIn("metadata", chunks[0])
    
    def test_process_pdf_utility(self):
        """Test the utility function."""
        # Skip this test until we have better mocks
        self.skipTest("Needs better PDF mocking")


if __name__ == "__main__":
    unittest.main()