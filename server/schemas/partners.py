from datetime import datetime

from pydantic import BaseModel


class PartnerInviteCreate(BaseModel):
    partner_tenant_id: int


class PartnerCompanyOut(BaseModel):
    id: int
    tenant_id: int
    partner_tenant_id: int
    status: str
    requested_by_tenant_id: int
    created_at: datetime

    class Config:
        from_attributes = True
