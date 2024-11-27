# backend/wiki_processor/utils.py
import re
from typing import List, Dict
from pathlib import Path
import json

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for all operating systems.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename.lower()

def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        path (str): Directory path
        
    Returns:
        Path: Path object of the directory
    """
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def save_metadata(path: str, metadata: Dict) -> None:
    """
    Save metadata to a JSON file.
    
    Args:
        path (str): Path to save the metadata
        metadata (Dict): Metadata to save
    """
    path = Path(path)
    with path.open('w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

def load_metadata(path: str) -> Dict:
    """
    Load metadata from a JSON file.
    
    Args:
        path (str): Path to the metadata file
        
    Returns:
        Dict: Loaded metadata
    """
    path = Path(path)
    if not path.exists():
        return {}
    
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)