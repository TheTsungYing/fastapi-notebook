from pydantic import BaseModel, EmailStr
from typing import Optional

# Pydantic 模型
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class Login(BaseModel):
    username: str
    password: str