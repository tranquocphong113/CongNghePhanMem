from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database.db import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)
    project_id = Column(Integer, nullable=False, index=True)
    status = Column(String(30), nullable=False, default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
