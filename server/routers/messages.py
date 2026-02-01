from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models.message import Message
from database.models.project import Project, ProjectMember
from database.models.user import User
from schemas.message import MessageCreate, MessageOut
from security.jwt import get_current_user
from security.permissions import ROLE_TENANT_ADMIN

router = APIRouter(prefix="/messages", tags=["Messages"])


def get_project_or_404(db: Session, project_id: int, tenant_id: int) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.tenant_id == tenant_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def require_project_member(
    db: Session,
    project_id: int,
    current_user: User,
) -> None:
    if current_user.role == ROLE_TENANT_ADMIN:
        return
    membership = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Not a project member")


@router.post("", response_model=MessageOut, status_code=201)
def create_message(
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_project_or_404(db, payload.project_id, current_user.tenant_id)
    require_project_member(db, payload.project_id, current_user)

    message = Message(
        project_id=payload.project_id,
        sender_id=current_user.id,
        content=payload.content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.get("/{project_id}", response_model=list[MessageOut])
def list_messages(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_project_or_404(db, project_id, current_user.tenant_id)
    require_project_member(db, project_id, current_user)

    return (
        db.query(Message)
        .filter(Message.project_id == project_id)
        .order_by(Message.created_at.asc())
        .all()
    )
