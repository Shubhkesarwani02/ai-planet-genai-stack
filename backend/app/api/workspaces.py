from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import logging

from app.db.database import get_db
from app.db import crud, schemas
from app.api.auth import get_current_user
from app.workers.tasks import process_document_upload
from app.services.chroma_client import chroma_client

logger = logging.getLogger(__name__)
router = APIRouter()

def generate_default_workflow(workspace_id: str, collection_name: str) -> dict:
    """Generate default workflow JSON for new workspace"""
    return {
        "nodes": [
            {
                "id": "user-query-1",
                "type": "user-query",
                "data": {
                    "label": "User Query",
                    "description": "Entry point for user questions"
                },
                "position": {"x": 100, "y": 200}
            },
            {
                "id": "knowledge-base-1",
                "type": "knowledge-base",
                "data": {
                    "label": "Knowledge Base",
                    "description": "Document knowledge retrieval",
                    "chroma_collection": collection_name,
                    "workspace_id": workspace_id,
                    "top_k": 5
                },
                "position": {"x": 350, "y": 200}
            },
            {
                "id": "llm-engine-1",
                "type": "llm-engine",
                "data": {
                    "label": "LLM Engine",
                    "description": "AI reasoning and response generation",
                    "model": "gpt-4o-mini",
                    "provider": "openai",
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                "position": {"x": 600, "y": 200}
            },
            {
                "id": "output-1",
                "type": "output",
                "data": {
                    "label": "Chat Output",
                    "description": "Final response to user"
                },
                "position": {"x": 850, "y": 200}
            }
        ],
        "edges": [
            {
                "id": "edge-1-2",
                "source": "user-query-1",
                "target": "knowledge-base-1",
                "type": "default"
            },
            {
                "id": "edge-2-3",
                "source": "knowledge-base-1",
                "target": "llm-engine-1",
                "type": "default"
            },
            {
                "id": "edge-3-4",
                "source": "llm-engine-1",
                "target": "output-1",
                "type": "default"
            }
        ]
    }

@router.post("/upload-document", response_model=schemas.DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and process a document to create a new workspace"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Read file content
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file"
            )
        
        # Generate unique workspace ID and collection name
        workspace_uuid = str(uuid.uuid4())
        collection_name = f"workspace_{workspace_uuid}"
        
        # Generate default workflow
        workflow_json = generate_default_workflow(workspace_uuid, collection_name)
        
        # Create workspace in database
        workspace_data = schemas.WorkspaceCreate(
            name=file.filename,
            doc_name=file.filename,
            doc_metadata={"file_size": len(file_content), "content_type": file.content_type},
            chroma_workspace_id=collection_name,
            workflow_json=workflow_json
        )
        
        workspace = await crud.create_workspace(
            db=db,
            workspace=workspace_data,
            user_id=str(current_user.id)
        )
        
        # Process document in background
        if background_tasks:
            background_tasks.add_task(
                process_document_upload,
                file_content,
                file.filename,
                workspace_uuid
            )
        else:
            # Process synchronously if no background tasks available
            await process_document_upload(
                file_content,
                file.filename,
                workspace_uuid
            )
        
        return schemas.DocumentUploadResponse(
            workspace=workspace,
            message="Document uploaded successfully",
            processing_status="processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )

@router.post("/create", response_model=schemas.WorkspaceResponse)
async def create_workspace(
    workspace_data: schemas.WorkspaceCreateSimple,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new workspace without document upload"""
    try:
        # Generate unique workspace ID and collection name
        workspace_uuid = str(uuid.uuid4())
        collection_name = f"workspace_{workspace_uuid}"
        
        # Generate default workflow
        workflow_json = generate_default_workflow(workspace_uuid, collection_name)
        
        # Create workspace in database
        workspace_create = schemas.WorkspaceCreate(
            name=workspace_data.name,
            description=workspace_data.description,
            chroma_workspace_id=collection_name,
            workflow_json=workflow_json
        )
        
        workspace = await crud.create_workspace(
            db=db,
            workspace=workspace_create,
            user_id=str(current_user.id)
        )
        
        return workspace
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating workspace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workspace"
        )

@router.get("/", response_model=List[schemas.WorkspaceResponse])
async def get_user_workspaces(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all workspaces for the current user"""
    try:
        workspaces = await crud.get_user_workspaces(db, user_id=str(current_user.id))
        return workspaces
    except Exception as e:
        logger.error(f"Error getting user workspaces: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workspaces"
        )

@router.get("/{workspace_id}", response_model=schemas.WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific workspace by ID"""
    try:
        workspace = await crud.get_workspace_by_id(
            db, 
            workspace_id=workspace_id, 
            user_id=str(current_user.id)
        )
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        return workspace
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workspace: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workspace"
        )

@router.put("/{workspace_id}/workflow", response_model=schemas.WorkspaceResponse)
async def update_workspace_workflow(
    workspace_id: str,
    workflow_update: schemas.WorkspaceUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update workspace workflow JSON"""
    try:
        if not workflow_update.workflow_json:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow JSON is required"
            )
        
        workspace = await crud.update_workspace_workflow(
            db,
            workspace_id=workspace_id,
            workflow_json=workflow_update.workflow_json,
            user_id=str(current_user.id)
        )
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        return workspace
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workspace workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update workspace workflow"
        )

@router.get("/{workspace_id}/info")
async def get_workspace_info(
    workspace_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get workspace information including ChromaDB collection info"""
    try:
        workspace = await crud.get_workspace_by_id(
            db, 
            workspace_id=workspace_id, 
            user_id=str(current_user.id)
        )
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found"
            )
        
        # Get ChromaDB collection info
        collection_info = chroma_client.get_collection_info(workspace.chroma_workspace_id)
        
        return {
            "workspace": workspace,
            "collection_info": collection_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workspace info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve workspace information"
        )