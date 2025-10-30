from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str

class UserOut(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime

    class Config:
        orm_mode = True