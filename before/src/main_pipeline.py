"""
Main pipeline orchestrator
Coordinates scraping, processing, and RAG operations
"""

import json
import os
from typing import List, Dict, Optional
from src.utils.scraper import LegalDocumentScraper
from src.models.document_processor import DocumentProcessor
from src.models.rag_engine import PineconeRAGEngine


class RAGPipeline:
    """
    Main pipeline for RAG chatbot
    """
    
    def __init__(
        self,
        openai_api_key: str,
        pinecone_api_key: str,
        pinecone_environment: str,
        index_name: str = "legal-documents"
    ):
        """
        Initialize the pipeline
        
        Args:
            openai_api_key: OpenAI API key
            pinecone_api_key: Pinecone API key
            pinecone_environment: Pinecone environment
            index_name: Pinecone index name
        """
        self.scraper = LegalDocumentScraper()
        self.processor = DocumentProcessor()
        self.rag_engine = PineconeRAGEngine(
            openai_api_key=openai_api_key,
            pinecone_api_key=pinecone_api_key,
            pinecone_environment=pinecone_environment,
            index_name=index_name
        )
        
        self.documents = []
        self.chunks = []
    
    def scrape_documents(self, max_documents: Optional[int] = None) -> List[Dict]:
        """
        Scrape legal documents from website
        
        Args:
            max_documents: Maximum number of documents to scrape
            
        Returns:
            List of scraped documents
        """
        print("Starting document scraping...")
        self.documents = self.scraper.scrape_all_documents(max_documents=max_documents)
        return self.documents
    
    def process_documents(self) -> List[Dict]:
        """
        Process scraped documents into chunks
        
        Returns:
            List of document chunks
        """
        if not self.documents:
            raise ValueError("No documents to process. Run scrape_documents() first.")
        
        print("Processing documents into chunks...")
        self.chunks = self.processor.process_documents(self.documents)
        return self.chunks
    
    def create_vector_store(self):
        """
        Create Pinecone index and store document chunks
        """
        if not self.chunks:
            raise ValueError("No chunks to store. Run process_documents() first.")
        
        print("Creating Pinecone index...")
        self.rag_engine.create_index()
        
        print("Storing documents in vector database...")
        self.rag_engine.store_documents(self.chunks)
    
    def load_existing_vector_store(self) -> bool:
        """
        Load existing Pinecone index
        
        Returns:
            True if successful, False otherwise
        """
        return self.rag_engine.load_existing_index()
    
    def query(self, question: str, temperature: float = 0.3) -> Dict:
        """
        Query the RAG system
        
        Args:
            question: User's question
            temperature: LLM temperature (0.0-1.0)
            
        Returns:
            Dictionary with answer and sources
        """
        return self.rag_engine.query(question, temperature=temperature)
    
    def save_documents(self, filepath: str = "data/scraped_documents.json"):
        """
        Save scraped documents to JSON
        
        Args:
            filepath: Output file path
        """
        if self.documents:
            self.scraper.save_to_json(self.documents, filepath)
    
    def load_documents(self, filepath: str = "data/scraped_documents.json") -> bool:
        """
        Load documents from JSON file
        
        Args:
            filepath: Input file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            print(f"Loaded {len(self.documents)} documents from {filepath}")
            return True
        except Exception as e:
            print(f"Error loading documents: {e}")
            return False
    
    def run_full_pipeline(self, max_documents: Optional[int] = None):
        """
        Run the complete pipeline: scrape, process, and store
        
        Args:
            max_documents: Maximum number of documents to scrape
        """
        # Step 1: Scrape documents
        self.scrape_documents(max_documents=max_documents)
        
        # Step 2: Save scraped documents
        self.save_documents()
        
        # Step 3: Process documents
        self.process_documents()
        
        # Step 4: Create vector store
        self.create_vector_store()
        
        print("\nPipeline completed successfully!")
        print(f"Total documents: {len(self.documents)}")
        print(f"Total chunks: {len(self.chunks)}")
    
    def get_stats(self) -> Dict:
        """
        Get pipeline statistics
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_documents": len(self.documents),
            "total_chunks": len(self.chunks),
            "index_stats": self.rag_engine.get_index_stats()
        }
        return stats
