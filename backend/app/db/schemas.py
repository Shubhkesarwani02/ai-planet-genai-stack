from pydantic import BaseModel, EmailStr
from typing import Optional, Any, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Workspace Schemas
class WorkspaceBase(BaseModel):
    name: str
    doc_name: Optional[str] = None
    doc_metadata: Optional[dict] = None

class WorkspaceCreate(WorkspaceBase):
    description: Optional[str] = None
    chroma_workspace_id: str
    workflow_json: Optional[dict] = None

class WorkspaceCreateSimple(BaseModel):
    name: str
    description: Optional[str] = None

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    workflow_json: Optional[dict] = None

class WorkspaceResponse(WorkspaceBase):
    id: str
    created_by: str
    description: Optional[str] = None
    chroma_workspace_id: str
    workflow_json: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessageCreate(BaseModel):
    workspace_id: str
    query: str

class ChatMessageResponse(BaseModel):
    id: str
    workspace_id: str
    created_by: str
    query: str
    response: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    response: str
    context_chunks: List[str]
    chat_log: ChatMessageResponse

# Document Upload Schema
class DocumentUploadResponse(BaseModel):
    workspace: WorkspaceResponse
    message: str
    processing_status: str