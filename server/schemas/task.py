from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int | None = None


class TaskStatusUpdate(BaseModel):
    status: str


class TaskOut(BaseModel):
    id: int
    title: str
    description: str | None
    status: str
    project_id: int
    assignee_id: int | None

    class Config:
        from_attributes = True
