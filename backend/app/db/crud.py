from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.db import models, schemas
from app.core.security import get_password_hash
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# User CRUD operations
def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
    """Get user by ID"""
    try:
        return db.query(models.User).filter(models.User.id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error getting user by ID {user_id}: {e}")
        return None

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email"""
    try:
        return db.query(models.User).filter(models.User.email == email).first()
    except SQLAlchemyError as e:
        logger.error(f"Error getting user by email {email}: {e}")
        return None

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    try:
        # Hash the password
        hashed_password = get_password_hash(user.password)
        
        # Create user instance
        db_user = models.User(
            email=user.email,
            name=user.name,
            password_hash=hashed_password
        )
        
        # Add to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Created new user with email: {user.email}")
        return db_user
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating user {user.email}: {e}")
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating user {user.email}: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating user {user.email}: {e}")
        raise

def update_user(db: Session, user_id: str, user_update: schemas.UserBase) -> Optional[models.User]:
    """Update user information (excluding password)"""
    try:
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        # Update fields if provided
        if user_update.email is not None:
            db_user.email = user_update.email
        if user_update.name is not None:
            db_user.name = user_update.name
        
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Updated user {user_id}")
        return db_user
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error updating user {user_id}: {e}")
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating user {user_id}: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating user {user_id}: {e}")
        raise

def update_user_password(db: Session, user_id: str, new_password: str) -> Optional[models.User]:
    """Update user password"""
    try:
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        # Hash the new password
        hashed_password = get_password_hash(new_password)
        db_user.password_hash = hashed_password
        
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"Updated password for user {user_id}")
        return db_user
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating password for user {user_id}: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating password for user {user_id}: {e}")
        raise

def delete_user(db: Session, user_id: str) -> bool:
    """Delete user by ID"""
    try:
        db_user = get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        
        logger.info(f"Deleted user {user_id}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting user {user_id}: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting user {user_id}: {e}")
        raise

# Workspace CRUD operations
def get_workspace_by_id(db: Session, workspace_id: str) -> Optional[models.Workspace]:
    """Get workspace by ID"""
    try:
        return db.query(models.Workspace).filter(models.Workspace.id == workspace_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Error getting workspace by ID {workspace_id}: {e}")
        return None

def get_user_workspaces(db: Session, user_id: str) -> list[models.Workspace]:
    """Get all workspaces for a user"""
    try:
        return db.query(models.Workspace).filter(models.Workspace.created_by == user_id).all()
    except SQLAlchemyError as e:
        logger.error(f"Error getting workspaces for user {user_id}: {e}")
        return []

def create_workspace(db: Session, workspace: schemas.WorkspaceCreate, user_id: str) -> models.Workspace:
    """Create a new workspace"""
    try:
        db_workspace = models.Workspace(
            created_by=user_id,
            name=workspace.name,
            doc_name=workspace.doc_name,
            doc_metadata=workspace.doc_metadata,
            chroma_workspace_id=workspace.chroma_workspace_id,
            workflow_json=workspace.workflow_json
        )
        
        db.add(db_workspace)
        db.commit()
        db.refresh(db_workspace)
        
        logger.info(f"Created new workspace {db_workspace.id} for user {user_id}")
        return db_workspace
        
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error creating workspace for user {user_id}: {e}")
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating workspace for user {user_id}: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating workspace for user {user_id}: {e}")
        raise

def update_workspace(db: Session, workspace_id: str, workspace_update: schemas.WorkspaceUpdate) -> Optional[models.Workspace]:
    """Update workspace information"""
    try:
        db_workspace = get_workspace_by_id(db, workspace_id)
        if not db_workspace:
            return None
        
        # Update fields if provided
        if workspace_update.name is not None:
            db_workspace.name = workspace_update.name
        if workspace_update.workflow_json is not None:
            db_workspace.workflow_json = workspace_update.workflow_json
        
        db.commit()
        db.refresh(db_workspace)
        
        logger.info(f"Updated workspace {workspace_id}")
        return db_workspace
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating workspace {workspace_id}: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating workspace {workspace_id}: {e}")
        raise

def delete_workspace(db: Session, workspace_id: str) -> bool:
    """Delete workspace by ID"""
    try:
        db_workspace = get_workspace_by_id(db, workspace_id)
        if not db_workspace:
            return False
        
        db.delete(db_workspace)
        db.commit()
        
        logger.info(f"Deleted workspace {workspace_id}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting workspace {workspace_id}: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting workspace {workspace_id}: {e}")
        raise

# Chat Log CRUD operations
def create_chat_log(db: Session, workspace_id: str, user_id: str, query: str, response: str) -> models.ChatLog:
    """Create a new chat log entry"""
    try:
        db_chat_log = models.ChatLog(
            workspace_id=workspace_id,
            created_by=user_id,
            query=query,
            response=response
        )
        
        db.add(db_chat_log)
        db.commit()
        db.refresh(db_chat_log)
        
        logger.info(f"Created chat log for workspace {workspace_id}")
        return db_chat_log
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating chat log: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating chat log: {e}")
        raise

def get_workspace_chat_logs(db: Session, workspace_id: str, limit: int = 50) -> list[models.ChatLog]:
    """Get chat logs for a workspace"""
    try:
        return (
            db.query(models.ChatLog)
            .filter(models.ChatLog.workspace_id == workspace_id)
            .order_by(models.ChatLog.created_at.desc())
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as e:
        logger.error(f"Error getting chat logs for workspace {workspace_id}: {e}")
        return []

def delete_chat_log(db: Session, chat_log_id: str) -> bool:
    """Delete chat log by ID"""
    try:
        db_chat_log = db.query(models.ChatLog).filter(models.ChatLog.id == chat_log_id).first()
        if not db_chat_log:
            return False
        
        db.delete(db_chat_log)
        db.commit()
        
        logger.info(f"Deleted chat log {chat_log_id}")
        return True
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error deleting chat log {chat_log_id}: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting chat log {chat_log_id}: {e}")
        raise
