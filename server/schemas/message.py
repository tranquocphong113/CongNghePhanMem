from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    project_id: int
    content: str


class MessageOut(BaseModel):
    id: int
    project_id: int
    sender_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
