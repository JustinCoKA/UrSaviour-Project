from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    # Accept camelCase on input
    email: EmailStr
    first_name: str = Field(validation_alias="firstName")
    last_name: str = Field(validation_alias="lastName")
    password: str

    model_config = ConfigDict(populate_by_name=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    # Output camelCase via serialization_alias
    user_id: str = Field(serialization_alias="userId")
    email: EmailStr
    first_name: str = Field(serialization_alias="firstName")
    last_name: str = Field(serialization_alias="lastName")
    created_at: datetime = Field(serialization_alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut