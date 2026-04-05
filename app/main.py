from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Review, ReviewReply, AdminUser
from .schemas import ReviewCreate, ReviewOut, ReplyCreate
from .auth import hash_password, verify_password

app = FastAPI(title="THEVOIR Reviews API")
templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/seed-admin")
def seed_admin(db: Session = Depends(get_db)):
    existing = db.query(AdminUser).filter(AdminUser.email == "admin@thevoir.com").first()
    if existing:
        return {"message": "Admin already exists"}

    admin = AdminUser(
        email="admin@thevoir.com",
        password_hash=hash_password("123456")
    )
    db.add(admin)
    db.commit()
    return {"message": "Admin created"}

@app.post("/reviews", response_model=ReviewOut)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db)):
    review = Review(
        product_handle=payload.product_handle,
        customer_name=payload.customer_name,
        rating=payload.rating,
        comment=payload.comment,
        approved=False
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@app.get("/reviews/{product_handle}", response_model=list[ReviewOut])
def get_reviews(product_handle: str, db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .filter(Review.product_handle == product_handle, Review.approved == True)
        .order_by(Review.created_at.desc())
        .all()
    )
    return reviews

@app.get("/admin/pending", response_model=list[ReviewOut])
def get_pending_reviews(db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .filter(Review.approved == False)
        .order_by(Review.created_at.desc())
        .all()
    )
    return reviews

@app.post("/admin/reviews/{review_id}/approve")
def approve_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.approved = True
    db.commit()
    return {"message": "Review approved"}

@app.post("/admin/reviews/{review_id}/reply")
def reply_review(review_id: int, payload: ReplyCreate, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    reply = ReviewReply(
        review_id=review_id,
        admin_name=payload.admin_name,
        reply_text=payload.reply_text
    )
    db.add(reply)
    db.commit()
    return {"message": "Reply added"}

@app.get("/admin-login", response_class=HTMLResponse)
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin-login")
def admin_login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.email == email).first()
    if not admin or not verify_password(password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"message": "Login successful", "email": admin.email}