import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

class ChromaDBClient:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            # Ensure persist directory exists
            os.makedirs(settings.chroma_persist_directory, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=settings.chroma_persist_directory
            )
            
            logger.info(f"ChromaDB client initialized with persist directory: {settings.chroma_persist_directory}")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {e}")
            raise
    
    def get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Get or create a ChromaDB collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            ChromaDB collection object
        """
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.info(f"Got/created collection: {collection_name}")
            return collection
            
        except Exception as e:
            logger.error(f"Error getting/creating collection {collection_name}: {e}")
            raise
    
    def add_documents(
        self, 
        collection_name: str, 
        documents: List[str], 
        embeddings: Optional[List[List[float]]] = None, 
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Add documents to a collection (with or without embeddings)
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            embeddings: Optional list of embedding vectors (None for text-only storage)
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            True if successful
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            # Generate IDs if not provided
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]
            
            # Generate default metadata if not provided
            if metadatas is None:
                metadatas = [{"index": i} for i in range(len(documents))]
            
            # Add documents to collection
            if embeddings is not None:
                # With embeddings
                collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                logger.info(f"Added {len(documents)} documents with embeddings to collection {collection_name}")
            else:
                # Without embeddings (text-only for later text search)
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                logger.info(f"Added {len(documents)} documents without embeddings to collection {collection_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to collection {collection_name}: {e}")
            raise
    
    def query_collection(
        self, 
        collection_name: str, 
        query_embeddings: List[List[float]], 
        n_results: int = 5,
        include: List[str] = None
    ) -> Dict[str, Any]:
        """
        Query a collection with embedding vectors
        
        Args:
            collection_name: Name of the collection
            query_embeddings: List of query embedding vectors
            n_results: Number of results to return
            include: List of fields to include in results
            
        Returns:
            Query results
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            if include is None:
                include = ["documents", "metadatas", "distances"]
            
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                include=include
            )
            
            logger.info(f"Queried collection {collection_name}, got {len(results.get('documents', []))} result sets")
            return results
            
        except Exception as e:
            logger.error(f"Error querying collection {collection_name}: {e}")
            raise
    
    def query_with_text(
        self, 
        collection_name: str, 
        query_texts: List[str], 
        n_results: int = 5,
        include: List[str] = None
    ) -> Dict[str, Any]:
        """
        Query a collection with text (ChromaDB will generate embeddings)
        
        Args:
            collection_name: Name of the collection
            query_texts: List of query texts
            n_results: Number of results to return
            include: List of fields to include in results
            
        Returns:
            Query results
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            
            if include is None:
                include = ["documents", "metadatas", "distances"]
            
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                include=include
            )
            
            logger.info(f"Text-queried collection {collection_name}, got {len(results.get('documents', []))} result sets")
            return results
            
        except Exception as e:
            logger.error(f"Error text-querying collection {collection_name}: {e}")
            raise
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get information about a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection information
        """
        try:
            collection = self.get_or_create_collection(collection_name)
            count = collection.count()
            
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info for {collection_name}: {e}")
            return {"name": collection_name, "count": 0, "error": str(e)}
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False

# Global ChromaDB client instance
chroma_client = ChromaDBClient()