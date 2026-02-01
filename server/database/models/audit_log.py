from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database.db import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    action = Column(String(50), nullable=False)
    details = Column(String(255), nullable=True)
    project_id = Column(Integer, nullable=True, index=True)
    task_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
