import asyncio
import uuid
from typing import Dict, Any, List
from app.services.pdf_utils import extract_text_from_pdf_bytes
from app.services.chunking import chunk_text_simple
from app.services.embeddings import embedding_service
from app.services.chroma_client import chroma_client
import logging

logger = logging.getLogger(__name__)

async def process_document_upload(
    file_bytes: bytes,
    file_name: str,
    workspace_id: str,
    embedding_provider: str = "gemini",
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> Dict[str, Any]:
    """
    Complete document processing pipeline
    
    Args:
        file_bytes: PDF file as bytes
        file_name: Original filename
        workspace_id: Unique workspace identifier
        embedding_provider: "openai" or "gemini"
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        
    Returns:
        Processing results and metadata
    """
    try:
        logger.info(f"Starting document processing for workspace {workspace_id}")
        
        # Step 1: Extract text from PDF
        extraction_result = extract_text_from_pdf_bytes(file_bytes, file_name)
        
        if not extraction_result["metadata"]["extraction_success"]:
            raise Exception(f"PDF extraction failed: {extraction_result['metadata'].get('error', 'Unknown error')}")
        
        text = extraction_result["text"]
        if not text.strip():
            raise Exception("No text content found in PDF")
        
        # Step 2: Chunk the text
        chunks = chunk_text_simple(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        if not chunks:
            raise Exception("No valid chunks created from text")
        
        logger.info(f"Created {len(chunks)} text chunks")
        
        # Step 3: Generate embeddings
        embeddings = await embedding_service.get_embeddings(
            chunks, 
            provider=embedding_provider
        )
        
        if len(embeddings) != len(chunks):
            raise Exception(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
        
        # Step 4: Store in ChromaDB
        collection_name = f"workspace_{workspace_id}"
        
        # Generate document IDs
        doc_ids = [f"chunk_{i}_{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
        
        # Create metadata for each chunk
        metadatas = [
            {
                "chunk_index": i,
                "workspace_id": workspace_id,
                "file_name": file_name,
                "chunk_size": len(chunk),
                "embedding_provider": embedding_provider
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Add to ChromaDB
        success = chroma_client.add_documents(
            collection_name=collection_name,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=doc_ids
        )
        
        if not success:
            raise Exception("Failed to store documents in ChromaDB")
        
        # Step 5: Return processing results
        result = {
            "success": True,
            "workspace_id": workspace_id,
            "collection_name": collection_name,
            "file_metadata": extraction_result["metadata"],
            "processing_stats": {
                "total_chunks": len(chunks),
                "total_characters": len(text),
                "average_chunk_size": sum(len(chunk) for chunk in chunks) / len(chunks),
                "embedding_provider": embedding_provider,
                "embedding_dimension": len(embeddings[0]) if embeddings else 0
            }
        }
        
        logger.info(f"Document processing completed successfully for workspace {workspace_id}")
        return result
        
    except Exception as e:
        logger.error(f"Document processing failed for workspace {workspace_id}: {e}")
        return {
            "success": False,
            "workspace_id": workspace_id,
            "error": str(e)
        }

async def query_workspace_knowledge(
    workspace_id: str,
    query: str,
    top_k: int = 5,
    embedding_provider: str = "gemini"
) -> Dict[str, Any]:
    """
    Query workspace knowledge base
    
    Args:
        workspace_id: Workspace identifier
        query: Query text
        top_k: Number of results to return
        embedding_provider: Embedding provider used
        
    Returns:
        Query results with context chunks
    """
    try:
        logger.info(f"Querying workspace {workspace_id} with query: {query[:100]}...")
        
        # Generate query embedding
        query_embedding = await embedding_service.get_query_embedding(
            query, 
            provider=embedding_provider
        )
        
        if not query_embedding:
            raise Exception("Failed to generate query embedding")
        
        # Query ChromaDB
        collection_name = f"workspace_{workspace_id}"
        
        results = chroma_client.query_collection(
            collection_name=collection_name,
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Extract results
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        # Format context chunks
        context_chunks = []
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            context_chunks.append({
                "text": doc,
                "metadata": metadata,
                "similarity_score": 1 - distance,  # Convert distance to similarity
                "rank": i + 1
            })
        
        result = {
            "success": True,
            "workspace_id": workspace_id,
            "query": query,
            "context_chunks": context_chunks,
            "total_results": len(context_chunks)
        }
        
        logger.info(f"Query completed, found {len(context_chunks)} relevant chunks")
        return result
        
    except Exception as e:
        logger.error(f"Query failed for workspace {workspace_id}: {e}")
        return {
            "success": False,
            "workspace_id": workspace_id,
            "query": query,
            "error": str(e),
            "context_chunks": []
        }