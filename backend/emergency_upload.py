#!/usr/bin/env python3
"""
Emergency document re-processor - uploads documents without embeddings for text search
"""

import asyncio
import os
from app.services.pdf_utils import extract_text_from_pdf_bytes
from app.services.chunking import chunk_text_simple
from app.services.chroma_client import chroma_client

async def emergency_process_pdf(file_path, workspace_id):
    """Process a PDF file and store without embeddings"""
    
    try:
        print(f"🔄 Processing PDF: {file_path}")
        print(f"📁 Workspace ID: {workspace_id}")
        
        # Read the PDF file
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        
        file_name = os.path.basename(file_path)
        
        # Extract text
        print("📖 Extracting text from PDF...")
        extraction_result = extract_text_from_pdf_bytes(file_bytes, file_name)
        
        if not extraction_result.get("success", False):
            print(f"❌ Failed to extract text: {extraction_result.get('error', 'Unknown error')}")
            return False
        
        text = extraction_result["text"]
        print(f"✅ Extracted {len(text)} characters")
        
        # Create chunks
        print("✂️ Chunking text...")
        chunks = chunk_text_simple(text, chunk_size=1000, overlap=200)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Store in ChromaDB without embeddings
        print("💾 Storing in ChromaDB without embeddings...")
        collection_name = f"workspace_{workspace_id}"
        
        # Generate document IDs
        doc_ids = [f"emergency_chunk_{i}_{file_name}" for i in range(len(chunks))]
        
        # Create metadata
        metadatas = [
            {
                "chunk_index": i,
                "workspace_id": workspace_id,
                "file_name": file_name,
                "chunk_size": len(chunk),
                "has_embeddings": False,
                "processing_mode": "emergency_text_only",
                "upload_timestamp": str(asyncio.get_event_loop().time())
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # Store without embeddings
        success = chroma_client.add_documents(
            collection_name=collection_name,
            documents=chunks,
            embeddings=None,  # No embeddings
            metadatas=metadatas,
            ids=doc_ids
        )
        
        if success:
            print(f"✅ Successfully stored {len(chunks)} document chunks!")
            
            # Test search
            print("🔍 Testing text search...")
            results = chroma_client.query_with_text(
                collection_name=collection_name,
                query_texts=["what"],
                n_results=3,
                include=["documents", "metadatas", "distances"]
            )
            
            found_docs = results.get("documents", [[]])[0]
            print(f"   Found {len(found_docs)} results for test query")
            
            return True
        else:
            print("❌ Failed to store documents")
            return False
            
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python emergency_upload.py <pdf_file_path> <workspace_id>")
        print("Example: python emergency_upload.py document.pdf 35e3cb53-9f6f-44ed-8902-7f8d20d4a4f6")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    workspace_id = sys.argv[2]
    
    if not os.path.exists(pdf_file):
        print(f"❌ File not found: {pdf_file}")
        sys.exit(1)
    
    print("🚨 Emergency Document Upload (Text-Only Mode)")
    print("=" * 50)
    
    success = asyncio.run(emergency_process_pdf(pdf_file, workspace_id))
    
    if success:
        print("\n✅ Emergency upload completed successfully!")
        print("💡 Your documents are now available for text-based search.")
    else:
        print("\n❌ Emergency upload failed!")