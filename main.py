from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://postgres:7683033Hal.@db.vfjjnuxjwbirfjtcwzqo.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_slug = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    status = Column(String, default="approved")

Base.metadata.create_all(bind=engine)

class ReviewCreate(BaseModel):
    product_slug: str
    customer_name: str
    rating: int
    comment: str
    image_url: str | None = None

@app.get("/")
def root():
    return {"message": "THEVOIR Reviews API çalışıyor"}

@app.post("/reviews")
def create_review(payload: ReviewCreate):
    db = SessionLocal()
    review = Review(
        product_slug=payload.product_slug,
        customer_name=payload.customer_name,
        rating=payload.rating,
        comment=payload.comment,
        image_url=payload.image_url,
        status="approved"
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    db.close()
    return review

@app.get("/reviews/{product_slug}")
def get_reviews(product_slug: str):
    db = SessionLocal()
    reviews = db.query(Review).filter(
        Review.product_slug == product_slug,
        Review.status == "approved"
    ).all()
    db.close()
    return reviews