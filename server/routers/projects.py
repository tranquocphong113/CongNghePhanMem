from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.audit import log_action
from database.db import get_db
from database.models.project import Project, ProjectMember
from database.models.user import User
from schemas.project import ProjectCreate, ProjectInvite, ProjectOut, ProjectRoleUpdate, ProjectUpdate
from security.jwt import get_current_user
from security.permissions import (
    ROLE_SYSTEM_ADMIN,
    ROLE_TENANT_ADMIN,
    ROLE_PM,
    ROLE_BA,
    ROLE_SUPPORT,
    ROLE_DEV,
    ROLE_QA,
    ROLE_CUSTOMER,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_or_404(db: Session, project_id: int, tenant_id: int) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.tenant_id == tenant_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def get_membership(db: Session, project_id: int, user_id: int) -> ProjectMember | None:
    return (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .first()
    )


@router.get("", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == ROLE_SYSTEM_ADMIN:
        raise HTTPException(status_code=403, detail="SYSTEM_ADMIN has no projects")

    if current_user.role in {ROLE_TENANT_ADMIN, ROLE_PM, ROLE_BA, ROLE_SUPPORT}:
        return db.query(Project).filter(Project.tenant_id == current_user.tenant_id).all()

    if current_user.role in {ROLE_DEV, ROLE_QA, ROLE_CUSTOMER}:
        return (
            db.query(Project)
            .join(ProjectMember)
            .filter(
                Project.tenant_id == current_user.tenant_id,
                ProjectMember.user_id == current_user.id,
            )
            .all()
        )

    raise HTTPException(status_code=403, detail="Not enough permissions")


@router.post("", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {ROLE_TENANT_ADMIN, ROLE_PM, ROLE_CUSTOMER}:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    project = Project(
        name=payload.name,
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    member = ProjectMember(
        user_id=current_user.id,
        project_id=project.id,
        role_in_project=ROLE_PM,
    )
    db.add(member)
    db.commit()

    log_action(db, current_user.id, "CREATE_PROJECT", project_id=project.id)
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != ROLE_PM:
        raise HTTPException(status_code=403, detail="Only PM can update projects")

    project = get_project_or_404(db, project_id, current_user.tenant_id)
    membership = get_membership(db, project_id, current_user.id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a project member")

    project.name = payload.name
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != ROLE_PM:
        raise HTTPException(status_code=403, detail="Only PM can delete projects")

    project = get_project_or_404(db, project_id, current_user.tenant_id)
    membership = get_membership(db, project_id, current_user.id)
    if not membership:
        raise HTTPException(status_code=403, detail="Not a project member")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted"}


@router.post("/{project_id}/invite")
def invite_member(
    project_id: int,
    payload: ProjectInvite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {ROLE_PM, ROLE_TENANT_ADMIN}:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    project = get_project_or_404(db, project_id, current_user.tenant_id)
    if current_user.role == ROLE_PM:
        membership = get_membership(db, project_id, current_user.id)
        if not membership:
            raise HTTPException(status_code=403, detail="Not a project member")

    user = (
        db.query(User)
        .filter(User.id == payload.user_id, User.tenant_id == current_user.tenant_id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = get_membership(db, project.id, user.id)
    if existing:
        raise HTTPException(status_code=400, detail="User already invited")

    member = ProjectMember(
        user_id=user.id,
        project_id=project.id,
        role_in_project=payload.role_in_project,
    )
    db.add(member)
    db.commit()
    return {"message": "User invited"}


@router.put("/{project_id}/members/{user_id}/role")
def update_member_role(
    project_id: int,
    user_id: int,
    payload: ProjectRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {ROLE_PM, ROLE_TENANT_ADMIN}:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    get_project_or_404(db, project_id, current_user.tenant_id)
    if current_user.role == ROLE_PM:
        membership = get_membership(db, project_id, current_user.id)
        if not membership:
            raise HTTPException(status_code=403, detail="Not a project member")

    member = get_membership(db, project_id, user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    member.role_in_project = payload.role_in_project
    db.commit()
    return {"message": "Role updated"}
