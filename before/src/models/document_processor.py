"""
Document processor for RAG pipeline
Handles text chunking, cleaning, and preprocessing
"""

from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re


class DocumentProcessor:
    """
    Process documents for RAG pipeline
    """
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        """
        Initialize document processor
        
        Args:
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\']', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_document(self, document: Dict) -> List[Dict]:
        """
        Split document into chunks with metadata
        
        Args:
            document: Document dictionary with 'content', 'title', 'url', etc.
            
        Returns:
            List of chunk dictionaries
        """
        content = document.get('content', '')
        
        if not content:
            return []
        
        # Clean the content
        cleaned_content = self.clean_text(content)
        
        # Split into chunks
        chunks = self.text_splitter.split_text(cleaned_content)
        
        # Create chunk dictionaries with metadata
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                'text': chunk_text,
                'metadata': {
                    'title': document.get('title', 'Untitled'),
                    'url': document.get('url', ''),
                    'category': document.get('category', 'Unknown'),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'source': 'legaldesk.com'
                }
            }
            chunk_dicts.append(chunk_dict)
        
        return chunk_dicts
    
    def process_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Process multiple documents into chunks
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of all chunks from all documents
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        print(f"Processed {len(documents)} documents into {len(all_chunks)} chunks")
        
        return all_chunks
