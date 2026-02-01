from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str


class ProjectUpdate(BaseModel):
    name: str


class ProjectOut(BaseModel):
    id: int
    name: str
    tenant_id: int
    created_by: int

    class Config:
        from_attributes = True


class ProjectInvite(BaseModel):
    user_id: int
    role_in_project: str


class ProjectRoleUpdate(BaseModel):
    role_in_project: str
