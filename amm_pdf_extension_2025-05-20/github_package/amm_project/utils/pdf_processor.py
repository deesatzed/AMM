"""
PDF Processing module for extracting and chunking text from PDF files.
"""

import os
import re
import io
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import uuid
import logging

# Initialize logger
logger = logging.getLogger("pdf_processor")

class PDFProcessor:
    """Processes PDF files into knowledge chunks for the AMM system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the PDF processor with configuration options.
        
        Args:
            config: Dictionary of configuration options:
                - chunk_size: Maximum characters per chunk (default: 1000)
                - chunk_overlap: Overlap between chunks (default: 200)
                - min_chunk_size: Minimum chunk size to keep (default: 50)
        """
        self.config = config or {}
        self.chunk_size = self.config.get("chunk_size", 1000)
        self.chunk_overlap = self.config.get("chunk_overlap", 200)
        self.min_chunk_size = self.config.get("min_chunk_size", 50)
        
        # Try to import PDF libraries - using try/except for graceful
        # handling if some libraries aren't available
        try:
            import PyPDF2
            self.PyPDF2 = PyPDF2
        except ImportError:
            logger.warning("PyPDF2 not available. Basic PDF support limited.")
            self.PyPDF2 = None
            
        try:
            import pdfplumber
            self.pdfplumber = pdfplumber
        except ImportError:
            logger.warning("pdfplumber not available. Layout preservation will be limited.")
            self.pdfplumber = None
            
        # OCR support is optional
        try:
            import pytesseract
            from pdf2image import convert_from_path
            self.pytesseract = pytesseract
            self.convert_from_path = convert_from_path
        except ImportError:
            logger.warning("pytesseract/pdf2image not available. OCR for scanned PDFs not supported.")
            self.pytesseract = None
            self.convert_from_path = None
    
    def detect_pdf_type(self, file_path: str) -> str:
        """Detect the type of PDF (text-based or scanned/image-based).
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            String indicating 'text', 'scanned', or 'unknown'
        """
        # Default to unknown
        pdf_type = "unknown"
        
        # Basic detection using PyPDF2
        if self.PyPDF2:
            try:
                with open(file_path, 'rb') as file:
                    reader = self.PyPDF2.PdfReader(file)
                    # Check a sample of pages
                    pages_to_check = min(3, len(reader.pages))
                    text_content = ""
                    
                    for i in range(pages_to_check):
                        page = reader.pages[i]
                        text_content += page.extract_text() or ""
                    
                    # If we extracted a reasonable amount of text, it's probably a text PDF
                    if len(text_content.strip()) > 100:
                        pdf_type = "text"
                    else:
                        # Likely a scanned document if little text was extracted
                        pdf_type = "scanned"
            except Exception as e:
                logger.error(f"Error detecting PDF type: {e}")
        
        return pdf_type
    
    def process_file(self, file_path: str, ocr_if_needed: bool = True) -> List[Dict[str, Any]]:
        """Process a PDF file into knowledge chunks.
        
        Args:
            file_path: Path to the PDF file
            ocr_if_needed: Whether to use OCR if the PDF appears to be scanned
            
        Returns:
            List of knowledge chunks, each with text and metadata
        """
        file_path = str(file_path)  # Ensure string path
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            return []
        
        # Detect PDF type
        pdf_type = self.detect_pdf_type(file_path)
        logger.info(f"Detected PDF type: {pdf_type} for {file_path}")
        
        # Extract text based on detected type
        if pdf_type == "scanned" and ocr_if_needed and self.pytesseract:
            # Use OCR for scanned PDFs
            text = self._extract_text_with_ocr(file_path)
        else:
            # Use standard extraction for text PDFs
            text = self._extract_text(file_path)
        
        # If text extraction failed, return empty result
        if not text:
            logger.warning(f"No text extracted from PDF: {file_path}")
            return []
        
        # Chunk the extracted text
        chunks = self._chunk_text(text)
        
        # Create knowledge chunks with metadata
        knowledge_chunks = []
        file_name = os.path.basename(file_path)
        
        for i, chunk_text in enumerate(chunks):
            # Skip chunks that are too small
            if len(chunk_text) < self.min_chunk_size:
                continue
                
            chunk_id = f"pdf_{uuid.uuid4().hex[:8]}"
            knowledge_chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "source_type": "pdf",
                "metadata": {
                    "file_name": file_name,
                    "content_type": "application/pdf",
                    "pdf_type": pdf_type,
                    "chunk_index": i,
                    "chunk_size": len(chunk_text),
                    "total_chunks": len(chunks)
                }
            })
        
        logger.info(f"Processed PDF into {len(knowledge_chunks)} chunks")
        return knowledge_chunks
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from a PDF using available libraries.
        
        Tries multiple extraction methods, using the best available.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        text = ""
        
        # Try pdfplumber first (better layout preservation)
        if self.pdfplumber:
            try:
                with self.pdfplumber.open(file_path) as pdf:
                    page_texts = []
                    for page in pdf.pages:
                        page_text = page.extract_text(x_tolerance=3) or ""
                        if page_text:
                            page_texts.append(page_text)
                    
                    text = "\n\n".join(page_texts)
                    
                    # If we got good results, return this text
                    if len(text.strip()) > 100:
                        return text
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}")
        
        # Fall back to PyPDF2 if needed
        if not text and self.PyPDF2:
            try:
                with open(file_path, 'rb') as file:
                    reader = self.PyPDF2.PdfReader(file)
                    page_texts = []
                    
                    for page in reader.pages:
                        page_text = page.extract_text() or ""
                        if page_text:
                            page_texts.append(page_text)
                    
                    text = "\n\n".join(page_texts)
            except Exception as e:
                logger.warning(f"PyPDF2 extraction failed: {e}")
        
        return text
    
    def _extract_text_with_ocr(self, file_path: str) -> str:
        """Extract text from a scanned PDF using OCR.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as a string
        """
        if not self.pytesseract or not self.convert_from_path:
            logger.error("OCR libraries not available")
            return ""
        
        try:
            # Convert PDF to images
            images = self.convert_from_path(file_path)
            
            # Perform OCR on each image
            page_texts = []
            for image in images:
                page_text = self.pytesseract.image_to_string(image)
                if page_text:
                    page_texts.append(page_text)
            
            return "\n\n".join(page_texts)
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of approximately chunk_size characters.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Clean text: normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Simple chunking strategy: split by paragraphs first,
        # then by sentences if paragraphs are too large
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        for paragraph in paragraphs:
            # If paragraph fits in current chunk, add it
            if len(current_chunk) + len(paragraph) <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += paragraph
            else:
                # If current chunk has content, add it to chunks
                if current_chunk:
                    chunks.append(current_chunk)
                
                # Check if paragraph needs to be split
                if len(paragraph) > self.chunk_size:
                    # Split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                    
                    current_chunk = ""
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) <= self.chunk_size:
                            if current_chunk:
                                current_chunk += " "
                            current_chunk += sentence
                        else:
                            # Save current chunk if it has content
                            if current_chunk:
                                chunks.append(current_chunk)
                            
                            # If sentence is longer than chunk_size, split it
                            if len(sentence) > self.chunk_size:
                                # Split long sentence into smaller pieces
                                for i in range(0, len(sentence), self.chunk_size - self.chunk_overlap):
                                    chunk = sentence[i:i + self.chunk_size]
                                    if len(chunk) >= self.min_chunk_size:
                                        chunks.append(chunk)
                                
                                current_chunk = ""
                            else:
                                current_chunk = sentence
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if it has content
        if current_chunk and len(current_chunk) >= self.min_chunk_size:
            chunks.append(current_chunk)
        
        return chunks

# Simple utility function for direct use
def process_pdf(file_path: str, **config) -> List[Dict[str, Any]]:
    """Utility function to process a PDF file with default settings.
    
    Args:
        file_path: Path to the PDF file
        **config: Optional configuration parameters
        
    Returns:
        List of knowledge chunks
    """
    processor = PDFProcessor(config)
    return processor.process_file(file_path)