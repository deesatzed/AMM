"""
File Handling Utilities
---------------------
Functions for handling file operations in the AMM GUI.
"""
import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Initialize logger
logger = logging.getLogger("file_handling")

# Try to import PDF libraries
try:
    from amm_project.utils.pdf_processor import process_pdf
    PDF_SUPPORT = True
except ImportError:
    logger.warning("PDF processor not available. PDF preview will be limited.")
    PDF_SUPPORT = False


def is_valid_knowledge_file(file_path: str, allowed_extensions: List[str] = None) -> bool:
    """
    Check if a file is valid for use as a knowledge source.
    
    Args:
        file_path: Path to the file
        allowed_extensions: List of allowed file extensions (without dot)
        
    Returns:
        True if the file is valid, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = ["txt", "md", "pdf"]
    
    path = Path(file_path)
    
    # Check if file exists
    if not path.exists():
        return False
    
    # Check if it's a file (not a directory)
    if not path.is_file():
        return False
    
    # Check file extension
    if path.suffix.lower()[1:] not in allowed_extensions:
        return False
    
    # Check if file is readable
    try:
        with open(path, 'r', encoding='utf-8') as f:
            f.read(1)  # Try to read one byte
        return True
    except:
        # File might not be readable as text (e.g., PDF)
        # Just check if we can open it
        try:
            with open(path, 'rb') as f:
                f.read(1)
            return True
        except:
            return False


def copy_knowledge_files(design_data: Dict[str, Any], target_dir: str) -> Dict[str, Any]:
    """
    Copy knowledge source files to a target directory and update paths in the design.
    
    Args:
        design_data: The AMM design data
        target_dir: Directory to copy files to
        
    Returns:
        Updated design data with new file paths
    """
    # Create a deep copy of the design data to avoid modifying the original
    import copy
    updated_design = copy.deepcopy(design_data)
    
    # Create the target directory if it doesn't exist
    knowledge_dir = Path(target_dir) / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each knowledge source
    for i, ks in enumerate(updated_design.get("knowledge_sources", [])):
        if ks.get("type") == "file" and "path" in ks:
            source_path = Path(ks["path"])
            
            if source_path.exists() and source_path.is_file():
                # Generate a target filename
                target_filename = f"{ks.get('id', f'ks_{i}')}{source_path.suffix}"
                target_path = knowledge_dir / target_filename
                
                # Copy the file
                try:
                    shutil.copy2(source_path, target_path)
                    
                    # Update the path in the design
                    updated_design["knowledge_sources"][i]["path"] = f"knowledge/{target_filename}"
                except Exception as e:
                    print(f"Error copying file {source_path}: {e}")
    
    return updated_design


def get_file_preview(file_path: str, max_chars: int = 1000) -> Tuple[bool, str]:
    """
    Get a preview of a file's contents.
    
    Args:
        file_path: Path to the file
        max_chars: Maximum number of characters to read
        
    Returns:
        Tuple of (success, content)
    """
    path = Path(file_path)
    
    if not path.exists() or not path.is_file():
        return False, "File not found"
    
    # Check if it's a PDF
    if path.suffix.lower() == '.pdf':
        # Try using PDF processor if available
        if PDF_SUPPORT:
            try:
                # Process the PDF and get the first chunk
                chunks = process_pdf(str(path), chunk_size=max_chars*2)
                if chunks and len(chunks) > 0:
                    # Take text from the first chunk
                    preview_text = chunks[0]["text"]
                    if len(preview_text) > max_chars:
                        preview_text = preview_text[:max_chars] + "...(truncated)"
                    
                    # Add some metadata about the PDF
                    pdf_info = (
                        f"PDF Type: {chunks[0]['metadata'].get('pdf_type', 'Unknown')}\n"
                        f"Total chunks: {len(chunks)}\n\n"
                        f"--- Content Preview ---\n{preview_text}"
                    )
                    return True, pdf_info
                else:
                    return False, "Unable to extract text from PDF (empty result)"
            except Exception as e:
                logger.error(f"Error processing PDF: {e}")
                return False, f"Error processing PDF: {str(e)}"
        else:
            # Basic binary file preview if PDF processor not available
            try:
                with open(path, 'rb') as f:
                    # Just check if we can read the file
                    f.read(10)
                return False, "PDF file detected (preview requires PDF processor)"
            except Exception as e:
                return False, f"Error opening PDF file: {str(e)}"
    
    # Standard text file handling
    try:
        # Try to read as text
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read(max_chars)
            if len(content) >= max_chars:
                content += "...(truncated)"
        return True, content
    except UnicodeDecodeError:
        # Not a text file
        return False, "Binary file (preview not available)"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"
