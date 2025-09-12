from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def chunk_text(
    text: str, 
    chunk_size: int = 500, 
    chunk_overlap: int = 50,
    separators: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Split text into chunks using RecursiveCharacterTextSplitter
    
    Args:
        text: Text to be chunked
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
        separators: List of separators to use for splitting
        
    Returns:
        List of dictionaries containing chunk data and metadata
    """
    try:
        if not text or not text.strip():
            return []
        
        # Default separators if none provided
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]
        
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=len,
        )
        
        # Split text into chunks
        chunks = text_splitter.split_text(text)
        
        # Create chunk objects with metadata
        chunk_objects = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():  # Only add non-empty chunks
                chunk_obj = {
                    "chunk_id": i,
                    "text": chunk,
                    "metadata": {
                        "chunk_index": i,
                        "chunk_size": len(chunk),
                        "start_char": text.find(chunk) if chunk in text else -1,
                        "end_char": text.find(chunk) + len(chunk) if chunk in text else -1,
                    }
                }
                chunk_objects.append(chunk_obj)
        
        logger.info(f"Successfully created {len(chunk_objects)} chunks from text of length {len(text)}")
        return chunk_objects
        
    except Exception as e:
        logger.error(f"Error chunking text: {e}")
        return []

def chunk_text_simple(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Simple text chunking that returns only the text strings
    
    Args:
        text: Text to be chunked
        chunk_size: Maximum size of each chunk
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    try:
        chunk_objects = chunk_text(text, chunk_size, chunk_overlap)
        return [chunk["text"] for chunk in chunk_objects]
    except Exception as e:
        logger.error(f"Error in simple chunking: {e}")
        return []

def get_chunking_stats(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get statistics about the chunking process
    
    Args:
        chunks: List of chunk objects
        
    Returns:
        Dictionary with chunking statistics
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "total_characters": 0,
            "average_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0
        }
    
    chunk_sizes = [len(chunk["text"]) for chunk in chunks]
    total_chars = sum(chunk_sizes)
    
    return {
        "total_chunks": len(chunks),
        "total_characters": total_chars,
        "average_chunk_size": total_chars / len(chunks),
        "min_chunk_size": min(chunk_sizes),
        "max_chunk_size": max(chunk_sizes)
    }