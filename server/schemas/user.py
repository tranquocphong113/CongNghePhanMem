from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreateAdmin(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    tenant_id: int
    is_locked: bool

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
