"""
Helper utility functions for the RAG application
"""

import os
from typing import List, Optional
import streamlit as st


def validate_api_key(api_key: Optional[str]) -> bool:
    """
    Validate if API key is provided and not empty
    
    Args:
        api_key: The API key to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return api_key is not None and len(api_key.strip()) > 0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def create_directory(path: str) -> bool:
    """
    Create directory if it doesn't exist
    
    Args:
        path: Directory path to create
        
    Returns:
        bool: True if created or exists, False on error
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        st.error(f"Error creating directory: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    
    Args:
        filename: Name of the file
        
    Returns:
        str: File extension (lowercase, without dot)
    """
    return os.path.splitext(filename)[1].lower().lstrip('.')
