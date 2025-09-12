from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.db.database import get_db
from app.db import crud, schemas
from app.api.auth import get_current_user
from app.workers.tasks import query_workspace_knowledge
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=schemas.ChatResponse)
async def chat_with_workspace(
    chat_request: schemas.ChatMessageCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get AI response based on workspace knowledge"""
    try:
        # Verify workspace exists and user has access
        workspace = await crud.get_workspace_by_id(
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
        knowledge_result = await query_workspace_knowledge(
            workspace_id=chat_request.workspace_id,
            query=chat_request.query,
            top_k=5,
            embedding_provider="openai"  # Could be made configurable
        )
        
        if not knowledge_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Knowledge retrieval failed: {knowledge_result.get('error', 'Unknown error')}"
            )
        
        # Extract context chunks
        context_chunks = [
            chunk["text"] for chunk in knowledge_result["context_chunks"]
        ]
        
        # Generate AI response
        try:
            ai_response = await llm_service.generate_response(
                query=chat_request.query,
                context_chunks=context_chunks,
                provider="openai",  # Could be made configurable
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=1000
            )
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            ai_response = "I apologize, but I'm currently unable to generate a response. Please try again later."
        
        # Save chat log to database
        chat_log = await crud.create_chat_log(
            db=db,
            chat=chat_request,
            response=ai_response,
            user_id=str(current_user.id)
        )
        
        # Return response with context
        return schemas.ChatResponse(
            response=ai_response,
            context_chunks=[chunk["text"] for chunk in knowledge_result["context_chunks"]],
            chat_log=chat_log
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
async def get_chat_history(
    workspace_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for a workspace"""
    try:
        # Verify workspace access
        workspace = await crud.get_workspace_by_id(
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
        chat_logs = await crud.get_workspace_chat_logs(
            db,
            workspace_id=workspace_id,
            user_id=str(current_user.id)
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
async def test_llm_connection(
    query: str = "Hello, how are you?",
    provider: str = "openai",
    current_user = Depends(get_current_user)
):
    """Test LLM connection and generation (for debugging)"""
    try:
        response = await llm_service.generate_response(
            query=query,
            context_chunks=[],
            provider=provider
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