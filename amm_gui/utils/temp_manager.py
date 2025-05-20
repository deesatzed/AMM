"""
Temporary File Manager
--------------------
Utilities for managing temporary files and directories in the AMM GUI.
"""
import os
import shutil
from pathlib import Path
import tempfile
from typing import Optional

def ensure_temp_dir(base_dir: Path, subdir: Optional[str] = None) -> Path:
    """
    Ensure a temporary directory exists and return its path.
    
    Args:
        base_dir: Base directory
        subdir: Optional subdirectory name
        
    Returns:
        Path to the temporary directory
    """
    temp_dir = base_dir / "temp"
    if subdir:
        temp_dir = temp_dir / subdir
    
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir

def clean_temp_files(base_dir: Path, pattern: str = "*", keep_days: int = 7) -> int:
    """
    Clean up old temporary files.
    
    Args:
        base_dir: Base directory
        pattern: File pattern to match
        keep_days: Number of days to keep files
        
    Returns:
        Number of files removed
    """
    import time
    
    temp_dir = base_dir / "temp"
    if not temp_dir.exists():
        return 0
    
    now = time.time()
    count = 0
    
    for path in temp_dir.glob(pattern):
        if path.is_file():
            # Check file age
            mtime = path.stat().st_mtime
            age_days = (now - mtime) / (60 * 60 * 24)
            
            if age_days > keep_days:
                path.unlink()
                count += 1
    
    return count

def create_zip_from_dir(source_dir: Path, zip_name: Optional[str] = None) -> Path:
    """
    Create a zip file from a directory.
    
    Args:
        source_dir: Directory to zip
        zip_name: Optional name for the zip file
        
    Returns:
        Path to the created zip file
    """
    if not source_dir.exists() or not source_dir.is_dir():
        raise ValueError(f"Source directory does not exist: {source_dir}")
    
    if not zip_name:
        zip_name = f"{source_dir.name}.zip"
    
    # Create a temporary directory for the zip file
    temp_dir = ensure_temp_dir(source_dir.parent)
    zip_path = temp_dir / zip_name
    
    # Remove existing zip file if it exists
    if zip_path.exists():
        zip_path.unlink()
    
    # Create the zip file
    shutil.make_archive(
        base_name=str(zip_path).replace(".zip", ""),
        format="zip",
        root_dir=source_dir
    )
    
    return zip_path
