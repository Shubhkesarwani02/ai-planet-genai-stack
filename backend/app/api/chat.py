from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging
import asyncio

from app.db.database import get_db
from app.db import crud, schemas
from app.api.auth import get_current_user
from app.workers.tasks import query_workspace_knowledge
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=schemas.ChatResponse)
def chat_with_workspace(
    chat_request: schemas.ChatMessageCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response based on workspace knowledge"""
    try:
        # Verify workspace exists and user has access
        workspace = crud.get_workspace_by_id(
            db,
            workspace_id=chat_request.workspace_id,
            user_id=str(current_user.id)
        )
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied"
            )
        
        # Query workspace knowledge base
        try:
            knowledge_result = asyncio.run(query_workspace_knowledge(
                workspace_id=chat_request.workspace_id,
                query=chat_request.query,
                top_k=5,
                embedding_provider="gemini"  # Use Gemini/Google
            ))
        except Exception as e:
            logger.error(f"Knowledge retrieval failed: {e}")
            knowledge_result = {"success": False, "error": str(e), "context_chunks": []}
        
        # Extract context chunks and metadata
        context_chunks = []
        warning_message = None
        search_method = "unknown"
        
        if knowledge_result.get("success", False):
            context_chunks = [
                chunk["text"] for chunk in knowledge_result.get("context_chunks", [])
            ]
            warning_message = knowledge_result.get("warning")
            search_method = knowledge_result.get("search_method", "unknown")
            document_count = knowledge_result.get("document_count", 0)
        else:
            warning_message = f"Knowledge retrieval failed: {knowledge_result.get('error', 'Unknown error')}"
            document_count = 0
        
        # Generate AI response using Gemini with context-aware prompting
        try:
            if not context_chunks and search_method == "no_documents":
                # Special handling for empty workspaces
                ai_response = llm_service.generate_response_sync(
                    query=f"""This is a question about a workspace that currently has no documents uploaded: "{chat_request.query}"
                    
Please respond helpfully by:
1. Acknowledging that no documents have been uploaded to this workspace yet
2. Explaining that you can still provide general information about the topic
3. Suggesting that the user upload relevant documents to get more specific, context-aware responses
4. Providing any general knowledge you have about their question

Answer the user's question to the best of your ability using general knowledge.""",
                    context_chunks=[],
                    provider="google",  # Use Gemini
                    model="gemini-2.0-flash-exp",
                    temperature=0.7,
                    max_tokens=1000
                )
            else:
                # Normal response with or without context
                context_info = ""
                if context_chunks:
                    context_info = f"Based on the {len(context_chunks)} most relevant document sections from your workspace, "
                else:
                    context_info = "Since no relevant documents were found in your workspace, I'll provide a general response. "
                
                query_with_context = f"{context_info}please answer this question: {chat_request.query}"
                
                ai_response = llm_service.generate_response_sync(
                    query=query_with_context,
                    context_chunks=context_chunks,
                    provider="google",  # Use Gemini
                    model="gemini-2.0-flash-exp",
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # Add information about the search method if relevant
                if warning_message:
                    ai_response += f"\n\n*Note: {warning_message}*"
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            ai_response = f"I apologize, but I'm currently unable to generate a response due to a technical issue: {str(e)}. Please try again later."
        
        # Save chat log to database
        try:
            chat_log = crud.create_chat_log(
                db=db,
                workspace_id=chat_request.workspace_id,
                user_id=str(current_user.id),
                query=chat_request.query,
                response=ai_response
            )
        except Exception as e:
            logger.error(f"Failed to save chat log: {e}")
            chat_log = None
        
        # Return response with context and metadata
        return schemas.ChatResponse(
            response=ai_response,
            context_chunks=context_chunks,
            chat_log=chat_log,
            metadata={
                "search_method": search_method,
                "document_count": document_count,
                "context_chunks_found": len(context_chunks),
                "warning": warning_message
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/{workspace_id}/history", response_model=List[schemas.ChatMessageResponse])
def get_chat_history(
    workspace_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a workspace"""
    try:
        # Verify workspace access
        workspace = crud.get_workspace_by_id(
            db,
            workspace_id=workspace_id,
            user_id=str(current_user.id)
        )
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied"
            )
        
        # Get chat logs
        chat_logs = crud.get_workspace_chat_logs(
            db,
            workspace_id=workspace_id
        )
        
        return chat_logs
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat history"
        )

@router.post("/test-llm")
def test_llm_connection(
    query: str = "Hello, how are you?",
    provider: str = "google",  # Use Gemini by default
    current_user = Depends(get_current_user)
):
    """Test LLM connection and generation (for debugging)"""
    try:
        response = llm_service.generate_response_sync(
            query=query,
            context_chunks=[],
            provider=provider,
            model="gemini-2.0-flash-exp" if provider == "google" else None
        )
        
        return {
            "success": True,
            "query": query,
            "response": response,
            "provider": provider
        }
        
    except Exception as e:
        logger.error(f"LLM test failed: {e}")
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "provider": provider
        }