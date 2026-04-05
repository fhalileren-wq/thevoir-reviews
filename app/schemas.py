from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ReplyOut(BaseModel):
    id: int
    admin_name: str
    reply_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    product_handle: str
    customer_name: str = Field(min_length=2, max_length=255)
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=3, max_length=2000)


class ReviewOut(BaseModel):
    id: int
    product_handle: str
    customer_name: str
    rating: int
    comment: str
    approved: bool
    created_at: datetime
    replies: List[ReplyOut] = []

    class Config:
        from_attributes = True


class ReplyCreate(BaseModel):
    admin_name: str
    reply_text: str = Field(min_length=1, max_length=2000)


class AdminLogin(BaseModel):
    email: str
    password: str