from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    role = Column(String(30), nullable=False)
    tenant_id = Column(Integer, nullable=False, index=True)
    is_locked = Column(Boolean, default=False)

    projects_created = relationship("Project", back_populates="creator")
    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    tasks_assigned = relationship("Task", back_populates="assignee")
