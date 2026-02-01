from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.audit import log_action
from database.db import get_db
from database.models.project import ProjectMember
from database.models.task import Task
from database.models.user import User
from schemas.user import (
    UserCreateAdmin,
    UserOut,
    UserRegister,
    TokenOut,
)
from security.jwt import create_access_token, get_current_user, hash_password, verify_password
from security.permissions import (
    ROLE_SYSTEM_ADMIN,
    ROLE_TENANT_ADMIN,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserOut)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    max_tenant_id = db.query(func.max(User.tenant_id)).scalar() or 0
    new_tenant_id = max_tenant_id + 1

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=ROLE_TENANT_ADMIN,
        tenant_id=new_tenant_id,
        is_locked=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.is_locked:
        raise HTTPException(status_code=403, detail="User is locked")

    token = create_access_token(user)
    log_action(db, user.id, "LOGIN", details="User login")
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=list[UserOut])
def list_users(
    role: str | None = Query(default=None, description="Filter by role"),
    tenant_id: int | None = Query(
        default=None,
        description="Filter by tenant id (SYSTEM_ADMIN only)",
    ),
    is_locked: bool | None = Query(
        default=None,
        description="Filter by lock status",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == ROLE_SYSTEM_ADMIN:
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        if tenant_id is not None:
            query = query.filter(User.tenant_id == tenant_id)
        if is_locked is not None:
            query = query.filter(User.is_locked == is_locked)
        return query.all()
    if current_user.role == ROLE_TENANT_ADMIN:
        if tenant_id is not None:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        query = db.query(User).filter(User.tenant_id == current_user.tenant_id)
        if role:
            query = query.filter(User.role == role)
        if is_locked is not None:
            query = query.filter(User.is_locked == is_locked)
        return query.all()
    raise HTTPException(status_code=403, detail="You do not have permission to create users")


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    payload: UserCreateAdmin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    if current_user.role == ROLE_SYSTEM_ADMIN:
        if payload.role not in {"TENANT_ADMIN", "PM", "DEV", "BA", "QA", "CUSTOMER"}:
            raise HTTPException(status_code=403, detail="You do not have permission to create users")
        max_tenant_id = db.query(func.max(User.tenant_id)).scalar() or 0
        tenant_id = max_tenant_id + 1
    elif current_user.role == ROLE_TENANT_ADMIN:
        if payload.role in {"SYSTEM_ADMIN", "TENANT_ADMIN"}:
            raise HTTPException(
                status_code=403,
                detail="TENANT_ADMIN cannot create SYSTEM_ADMIN or TENANT_ADMIN",
            )
        if payload.role not in {"PM", "DEV", "QA", "CUSTOMER"}:
            raise HTTPException(status_code=403, detail="You do not have permission to create users")
        tenant_id = current_user.tenant_id
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to create users")

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        tenant_id=tenant_id,
        is_locked=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == target_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    if current_user.role == ROLE_SYSTEM_ADMIN:
        pass
    elif current_user.role == ROLE_TENANT_ADMIN:
        if target_user.role == ROLE_SYSTEM_ADMIN:
            raise HTTPException(status_code=403, detail="Cannot delete SYSTEM_ADMIN")
        if target_user.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="User is not in your tenant")
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to delete users")

    db.query(ProjectMember).filter(ProjectMember.user_id == target_user.id).delete(
        synchronize_session=False
    )
    db.query(Task).filter(Task.assignee_id == target_user.id).update(
        {Task.assignee_id: None},
        synchronize_session=False,
    )
    db.delete(target_user)
    db.commit()
    return {"message": "User deleted successfully"}
