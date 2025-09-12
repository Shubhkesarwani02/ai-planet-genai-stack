from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc
from app.db.models import User, Workspace, ChatLog
from app.db.schemas import UserCreate, WorkspaceCreate, ChatMessageCreate
from passlib.context import CryptContext
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User CRUD operations
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    try:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None

async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID"""
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None

async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create new user"""
    try:
        hashed_password = pwd_context.hash(user.password)
        db_user = User(
            email=user.email,
            password_hash=hashed_password
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user: {e}")
        raise

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

# Workspace CRUD operations
async def create_workspace(db: AsyncSession, workspace: WorkspaceCreate, user_id: str) -> Workspace:
    """Create new workspace"""
    try:
        db_workspace = Workspace(
            created_by=user_id,
            name=workspace.name,
            doc_name=workspace.doc_name,
            doc_metadata=workspace.doc_metadata,
            chroma_workspace_id=workspace.chroma_workspace_id,
            workflow_json=workspace.workflow_json
        )
        db.add(db_workspace)
        await db.commit()
        await db.refresh(db_workspace)
        return db_workspace
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating workspace: {e}")
        raise

async def get_workspace_by_id(db: AsyncSession, workspace_id: str, user_id: str) -> Optional[Workspace]:
    """Get workspace by ID for specific user"""
    try:
        result = await db.execute(
            select(Workspace).where(
                and_(Workspace.id == workspace_id, Workspace.created_by == user_id)
            )
        )
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error getting workspace: {e}")
        return None

async def get_user_workspaces(db: AsyncSession, user_id: str) -> List[Workspace]:
    """Get all workspaces for a user"""
    try:
        result = await db.execute(
            select(Workspace)
            .where(Workspace.created_by == user_id)
            .order_by(desc(Workspace.created_at))
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error getting user workspaces: {e}")
        return []

async def update_workspace_workflow(db: AsyncSession, workspace_id: str, workflow_json: dict, user_id: str) -> Optional[Workspace]:
    """Update workspace workflow JSON"""
    try:
        result = await db.execute(
            select(Workspace).where(
                and_(Workspace.id == workspace_id, Workspace.created_by == user_id)
            )
        )
        workspace = result.scalars().first()
        if workspace:
            workspace.workflow_json = workflow_json
            await db.commit()
            await db.refresh(workspace)
        return workspace
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating workspace workflow: {e}")
        return None

# Chat CRUD operations
async def create_chat_log(db: AsyncSession, chat: ChatMessageCreate, response: str, user_id: str) -> ChatLog:
    """Create new chat log"""
    try:
        db_chat = ChatLog(
            workspace_id=chat.workspace_id,
            created_by=user_id,
            query=chat.query,
            response=response
        )
        db.add(db_chat)
        await db.commit()
        await db.refresh(db_chat)
        return db_chat
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating chat log: {e}")
        raise

async def get_workspace_chat_logs(db: AsyncSession, workspace_id: str, user_id: str) -> List[ChatLog]:
    """Get chat logs for a workspace"""
    try:
        result = await db.execute(
            select(ChatLog)
            .where(and_(ChatLog.workspace_id == workspace_id, ChatLog.created_by == user_id))
            .order_by(ChatLog.created_at)
        )
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error getting chat logs: {e}")
        return []