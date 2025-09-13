from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "app_users"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    workspaces = relationship("Workspace", back_populates="user")

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    created_by = Column(UUID(as_uuid=False), ForeignKey("app_users.id"), nullable=False)
    name = Column(Text, nullable=False)
    doc_name = Column(Text, nullable=True)
    doc_metadata = Column(JSON, nullable=True)
    chroma_workspace_id = Column(Text, unique=True, nullable=False)
    workflow_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="workspaces")
    chat_logs = relationship("ChatLog", back_populates="workspace")

class ChatLog(Base):
    __tablename__ = "chat_logs"
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    workspace_id = Column(UUID(as_uuid=False), ForeignKey("workspaces.id"), nullable=False)
    created_by = Column(UUID(as_uuid=False), ForeignKey("app_users.id"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    workspace = relationship("Workspace", back_populates="chat_logs")
    user = relationship("User")