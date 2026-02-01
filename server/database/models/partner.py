from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database.db import Base


class PartnerCompany(Base):
    __tablename__ = "partner_companies"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    partner_tenant_id = Column(Integer, nullable=False, index=True)
    status = Column(String(20), nullable=False, default="PENDING")
    requested_by_tenant_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
