import asyncio
import uuid
from typing import Dict, Any, List
from app.services.pdf_utils import extract_text_from_pdf_bytes
from app.services.chunking import chunk_text_simple
from app.services.embeddings import embedding_service
from app.services.chroma_client import chroma_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def process_document_upload(
    file_bytes: bytes,
    file_name: str,
    workspace_id: str,
    embedding_provider: str = "gemini",
    chunk_size: int = 800,  # Increased chunk size for fewer embeddings
    chunk_overlap: int = 100
) -> Dict[str, Any]:
    """
    Complete document processing pipeline with improved rate limiting
    
    Args:
        file_bytes: PDF file as bytes
        file_name: Original filename
        workspace_id: Unique workspace identifier
        embedding_provider: "openai" or "gemini"
        chunk_size: Size of text chunks (increased for fewer API calls)
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
        
        # Step 2: Chunk the text with larger chunks to reduce API calls
        chunks = chunk_text_simple(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        if not chunks:
            raise Exception("No valid chunks created from text")
        
        logger.info(f"Created {len(chunks)} text chunks (avg size: {sum(len(c) for c in chunks) // len(chunks)} chars)")
        
        # Step 3: Limit chunks for free tier APIs to avoid quota issues
        max_chunks_for_free_tier = settings.max_chunks_per_document  # Use configurable limit
        
        if len(chunks) > max_chunks_for_free_tier:
            logger.warning(f"Document has {len(chunks)} chunks, limiting to {max_chunks_for_free_tier} to avoid quota issues")
            # Take the first chunks which usually contain the most important content
            chunks = chunks[:max_chunks_for_free_tier]
            logger.info(f"Using first {len(chunks)} chunks for processing")
        
        # Step 4: Generate embeddings (with enhanced fallback handling)
        embeddings = None
        embedding_failed = False
        warning_message = None
        
        try:
            # Check provider availability first
            provider_status = embedding_service.check_provider_availability(embedding_provider)
            if not provider_status["available"]:
                logger.warning(f"Primary provider {embedding_provider} not available: {provider_status['reason']}")
                embedding_failed = True
                warning_message = f"Embedding provider not configured: {provider_status['reason']}"
            else:
                logger.info(f"Generating embeddings for {len(chunks)} chunks using {embedding_provider}")
                embeddings = await embedding_service.get_embeddings(
                    chunks, 
                    provider=embedding_provider
                )
                
                if len(embeddings) != len(chunks):
                    raise Exception(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
                    
                logger.info(f"Successfully generated {len(embeddings)} embeddings")
            
        except Exception as e:
            error_msg = str(e).lower()
            if any(keyword in error_msg for keyword in ['quota', 'rate limit', '429', 'resource_exhausted']):
                logger.warning(f"Embedding generation failed due to quota limits: {e}")
                warning_message = "Embeddings skipped due to API quota limits. Document stored for text search only."
            else:
                logger.warning(f"Embedding generation failed: {e}")
                warning_message = f"Embeddings failed: {str(e)}"
            
            logger.info("Storing documents without embeddings for text-based search")
            embedding_failed = True
            embeddings = None
        
        # Step 5: Store in ChromaDB (with or without embeddings)
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
                "embedding_provider": embedding_provider,
                "has_embeddings": not embedding_failed,
                "upload_timestamp": str(asyncio.get_event_loop().time()),
                "processing_mode": "text_only" if embedding_failed else "with_embeddings"
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
        
        # Step 6: Return processing results with detailed status
        result = {
            "success": True,
            "workspace_id": workspace_id,
            "file_name": file_name,
            "chunks_processed": len(chunks),
            "total_documents": len(chunks),
            "embeddings_generated": len(embeddings) if embeddings else 0,
            "storage_mode": "with_embeddings" if embeddings else "text_only",
            "embedding_provider": embedding_provider,
            "warning": warning_message,
            "collection_name": collection_name,
            "file_metadata": extraction_result["metadata"],
            "processing_stats": {
                "total_chunks": len(chunks),
                "total_characters": len(text),
                "average_chunk_size": sum(len(chunk) for chunk in chunks) / len(chunks),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                "chunk_size_used": chunk_size,
                "max_chunks_processed": max_chunks_for_free_tier if len(chunks) == max_chunks_for_free_tier else len(chunks)
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
    Query workspace knowledge base with enhanced empty workspace handling
    
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
        
        collection_name = f"workspace_{workspace_id}"
        
        # First check if collection has any documents
        collection_info = chroma_client.get_collection_info(collection_name)
        document_count = collection_info.get("count", 0)
        
        if document_count == 0:
            logger.info(f"Workspace {workspace_id} has no documents uploaded")
            return {
                "success": True,
                "workspace_id": workspace_id,
                "query": query,
                "context_chunks": [],
                "total_results": 0,
                "search_method": "no_documents",
                "warning": "This workspace has no documents uploaded. The AI will respond based on general knowledge only."
            }
        
        logger.info(f"Workspace {workspace_id} has {document_count} documents")
        
        # Try to generate query embedding
        try:
            query_embedding = await embedding_service.get_query_embedding(
                query, 
                provider=embedding_provider
            )
            
            if not query_embedding:
                raise Exception("Failed to generate query embedding")
            
            # Query ChromaDB with embeddings
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
            
            logger.info(f"Query completed with embeddings, found {len(context_chunks)} relevant chunks")
            search_method = "embedding"
            warning = None
            
        except Exception as embedding_error:
            # Check if it's a quota/rate limit error
            error_msg = str(embedding_error).lower()
            if any(keyword in error_msg for keyword in ['quota', 'rate limit', '429', 'exceeded', 'resource_exhausted']):
                logger.warning(f"Embedding service unavailable due to quota limits, falling back to text search: {embedding_error}")
                
                # Fallback to text-based search using ChromaDB's query_texts feature
                try:
                    # Use ChromaDB's text search capability  
                    results = chroma_client.query_with_text(
                        collection_name=collection_name,
                        query_texts=[query],
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
                            "rank": i + 1,
                            "search_method": "text_fallback"  # Indicate this was a fallback search
                        })
                    
                    logger.info(f"Fallback text search completed, found {len(context_chunks)} relevant chunks")
                    search_method = "text_fallback"
                    warning = "Using text-based search due to embedding quota limits. Results may be less accurate."
                    
                except Exception as fallback_error:
                    logger.error(f"Both embedding and text fallback searches failed: {fallback_error}")
                    # Return empty results but don't fail completely
                    context_chunks = []
                    search_method = "failed"
                    warning = f"Knowledge base search failed: {str(fallback_error)}"
            else:
                # Re-raise if it's not a quota issue
                raise embedding_error
        
        result = {
            "success": True,
            "workspace_id": workspace_id,
            "query": query,
            "context_chunks": context_chunks,
            "total_results": len(context_chunks),
            "search_method": search_method,
            "document_count": document_count,
            "warning": warning
        }
        
        logger.info(f"Query completed, found {len(context_chunks)} relevant chunks using method: {search_method}")
        return result
        
    except Exception as e:
        logger.error(f"Query failed for workspace {workspace_id}: {e}")
        return {
            "success": False,
            "workspace_id": workspace_id,
            "query": query,
            "error": str(e),
            "context_chunks": [],
            "document_count": 0
        }