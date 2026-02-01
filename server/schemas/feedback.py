from datetime import datetime

from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    title: str
    description: str
    project_id: int


class FeedbackStatusUpdate(BaseModel):
    status: str


class FeedbackOut(BaseModel):
    id: int
    title: str
    description: str
    customer_id: int
    project_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
