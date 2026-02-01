from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.db import get_db
from database.models.partner import PartnerCompany
from database.models.user import User
from schemas.partners import PartnerCompanyOut, PartnerInviteCreate
from security.jwt import get_current_user
from security.permissions import ROLE_TENANT_ADMIN, ROLE_PM

router = APIRouter(tags=["Partners"])

# Project-level partner request APIs removed to keep tenant-level partnerships only.
STATUS_PENDING = "PENDING"
STATUS_ACCEPTED = "ACCEPTED"
STATUS_REJECTED = "REJECTED"
STATUS_REVOKE_PENDING = "REVOKE_PENDING"


def tenant_exists(db: Session, tenant_id: int) -> bool:
    return db.query(User.id).filter(User.tenant_id == tenant_id).first() is not None


def normalize_pair(tenant_id: int, partner_tenant_id: int) -> tuple[int, int]:
    return (
        (tenant_id, partner_tenant_id)
        if tenant_id < partner_tenant_id
        else (partner_tenant_id, tenant_id)
    )


def get_partnership(db: Session, tenant_id: int, partner_tenant_id: int) -> PartnerCompany | None:
    left_id, right_id = normalize_pair(tenant_id, partner_tenant_id)
    return (
        db.query(PartnerCompany)
        .filter(
            PartnerCompany.tenant_id == left_id,
            PartnerCompany.partner_tenant_id == right_id,
        )
        .first()
    )


def require_tenant_admin(current_user: User) -> None:
    if current_user.role not in {ROLE_TENANT_ADMIN, ROLE_PM}:
        raise HTTPException(status_code=403, detail="Not enough permissions")


@router.post("/partners/request", response_model=PartnerCompanyOut)
def request_partner(
    payload: PartnerInviteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_tenant_admin(current_user)

    if payload.partner_tenant_id == current_user.tenant_id:
        raise HTTPException(status_code=400, detail="Cannot partner with your own tenant")
    if payload.partner_tenant_id <= 0 or not tenant_exists(db, payload.partner_tenant_id):
        raise HTTPException(status_code=404, detail="Partner tenant not found")

    existing = get_partnership(db, current_user.tenant_id, payload.partner_tenant_id)
    if existing:
        if existing.status == STATUS_ACCEPTED or existing.status == STATUS_REVOKE_PENDING:
            raise HTTPException(status_code=400, detail="Partnership already exists")
        if existing.status == STATUS_PENDING:
            raise HTTPException(status_code=400, detail="Request already pending")
        if existing.status == STATUS_REJECTED:
            existing.status = STATUS_PENDING
            existing.requested_by_tenant_id = current_user.tenant_id
            existing.created_at = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing

    left_id, right_id = normalize_pair(current_user.tenant_id, payload.partner_tenant_id)

    partnership = PartnerCompany(
        tenant_id=left_id,
        partner_tenant_id=right_id,
        status=STATUS_PENDING,
        requested_by_tenant_id=current_user.tenant_id,
    )
    db.add(partnership)
    db.commit()
    db.refresh(partnership)
    return partnership


@router.put("/partners/{partnership_id}/accept")
def accept_partner(
    partnership_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_tenant_admin(current_user)

    partnership = db.query(PartnerCompany).filter(PartnerCompany.id == partnership_id).first()
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")
    if partnership.status != STATUS_PENDING:
        raise HTTPException(status_code=400, detail="Partnership is not pending")
    if current_user.tenant_id not in {partnership.tenant_id, partnership.partner_tenant_id}:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if partnership.requested_by_tenant_id == current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Inviter cannot accept the invitation")

    partnership.status = STATUS_ACCEPTED
    db.commit()
    return {"message": "Partnership accepted"}


@router.put("/partners/{partnership_id}/reject")
def reject_partner(
    partnership_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_tenant_admin(current_user)

    partnership = db.query(PartnerCompany).filter(PartnerCompany.id == partnership_id).first()
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")
    if partnership.status != STATUS_PENDING:
        raise HTTPException(status_code=400, detail="Partnership is not pending")
    if current_user.tenant_id not in {partnership.tenant_id, partnership.partner_tenant_id}:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if partnership.requested_by_tenant_id == current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Inviter cannot reject the invitation")

    partnership.status = STATUS_REJECTED
    db.commit()
    return {"message": "Partnership rejected"}


@router.post("/partners/{partnership_id}/revoke")
def revoke_partnership(
    partnership_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_tenant_admin(current_user)

    partnership = db.query(PartnerCompany).filter(PartnerCompany.id == partnership_id).first()
    if not partnership:
        raise HTTPException(status_code=404, detail="Partnership not found")
    if current_user.tenant_id not in {partnership.tenant_id, partnership.partner_tenant_id}:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if partnership.status == STATUS_ACCEPTED:
        partnership.status = STATUS_REVOKE_PENDING
        partnership.requested_by_tenant_id = current_user.tenant_id
        db.commit()
        return {"message": "Revoke requested"}

    if partnership.status == STATUS_REVOKE_PENDING:
        if partnership.requested_by_tenant_id == current_user.tenant_id:
            raise HTTPException(status_code=400, detail="Waiting for other tenant to confirm")
        db.delete(partnership)
        db.commit()
        return {"message": "Partnership revoked"}

    raise HTTPException(status_code=400, detail="Partnership is not active")


@router.get("/partners", response_model=list[PartnerCompanyOut])
def list_partners(
    status: str | None = Query(default=None, description="Filter by status"),
    direction: str | None = Query(
        default=None,
        description="Filter by direction: INCOMING or OUTGOING",
    ),
    keyword: str | None = Query(default=None, description="Filter by partner name keyword"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_tenant_admin(current_user)

    query = (
        db.query(PartnerCompany)
        .filter(
            (
                (PartnerCompany.tenant_id == current_user.tenant_id)
                | (PartnerCompany.partner_tenant_id == current_user.tenant_id)
            ),
        )
    )

    if status:
        normalized_status = status.strip().upper()
        if normalized_status not in {STATUS_PENDING, STATUS_ACCEPTED, STATUS_REJECTED}:
            raise HTTPException(status_code=400, detail="Invalid status filter")
        query = query.filter(PartnerCompany.status == normalized_status)

    if direction:
        normalized_direction = direction.strip().upper()
        if normalized_direction not in {"INCOMING", "OUTGOING"}:
            raise HTTPException(status_code=400, detail="Invalid direction filter")
        if normalized_direction == "OUTGOING":
            query = query.filter(PartnerCompany.requested_by_tenant_id == current_user.tenant_id)
        else:
            query = query.filter(PartnerCompany.requested_by_tenant_id != current_user.tenant_id)

    if keyword:
        normalized_keyword = keyword.strip()
        if normalized_keyword:
            tenant_ids = [
                row[0]
                for row in (
                    db.query(User.tenant_id)
                    .filter(User.name.ilike(f"%{normalized_keyword}%"))
                    .distinct()
                    .all()
                )
            ]
            if not tenant_ids:
                return []
            query = query.filter(
                (
                    (PartnerCompany.tenant_id == current_user.tenant_id)
                    & (PartnerCompany.partner_tenant_id.in_(tenant_ids))
                )
                | (
                    (PartnerCompany.partner_tenant_id == current_user.tenant_id)
                    & (PartnerCompany.tenant_id.in_(tenant_ids))
                )
            )

    return query.all()
