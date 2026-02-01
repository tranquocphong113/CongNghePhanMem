from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models.feedback import Feedback
from database.models.project import Project, ProjectMember
from database.models.user import User
from schemas.feedback import FeedbackCreate, FeedbackOut, FeedbackStatusUpdate
from security.jwt import get_current_user
from security.permissions import (
    ROLE_TENANT_ADMIN,
    ROLE_PM,
    ROLE_BA,
    ROLE_SUPPORT,
    ROLE_CUSTOMER,
)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


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


@router.post("", response_model=FeedbackOut, status_code=201)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != ROLE_CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can submit feedback")

    get_project_or_404(db, payload.project_id, current_user.tenant_id)
    require_project_member(db, payload.project_id, current_user)

    feedback = Feedback(
        title=payload.title,
        description=payload.description,
        customer_id=current_user.id,
        project_id=payload.project_id,
        status="OPEN",
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


@router.get("/project/{project_id}", response_model=list[FeedbackOut])
def list_feedback_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_project_or_404(db, project_id, current_user.tenant_id)
    require_project_member(db, project_id, current_user)

    return db.query(Feedback).filter(Feedback.project_id == project_id).all()


@router.put("/{feedback_id}/status", response_model=FeedbackOut)
def update_feedback_status(
    feedback_id: int,
    payload: FeedbackStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {ROLE_TENANT_ADMIN, ROLE_PM, ROLE_BA, ROLE_SUPPORT}:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    get_project_or_404(db, feedback.project_id, current_user.tenant_id)
    if current_user.role != ROLE_TENANT_ADMIN:
        require_project_member(db, feedback.project_id, current_user)

    feedback.status = payload.status
    db.commit()
    db.refresh(feedback)
    return feedback
