import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from .db import Base, engine, get_db
from .models import Course, Lead, Payment, Student, Task, User

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
ALGORITHM = "HS256"
app = FastAPI(title="NexaCRM API", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def create_schema() -> None:
    if os.getenv("VERCEL") and not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL must point to PostgreSQL in Vercel")
    Base.metadata.create_all(bind=engine)

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240000)
    return salt.hex() + ":" + digest.hex()

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split(":", 1)
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 240000).hex()
        return hmac.compare_digest(candidate, digest)
    except ValueError:
        return False

def token_for(user: User) -> str:
    return jwt.encode({"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(days=7)}, SECRET_KEY, algorithm=ALGORITHM)

def current_user(request: Request, db: Session) -> User | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        user_id = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        return db.get(User, int(user_id)) if user_id else None
    except (JWTError, ValueError):
        return None

def require_user(request: Request, db: Session) -> User:
    user = current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required")
    return user

@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "database": os.getenv("DATABASE_URL", "sqlite")[:20]}

@app.get("/", response_class=HTMLResponse)
def landing(request: Request, db: Annotated[Session, Depends(get_db)]) -> str:
    user = current_user(request, db)
    if user:
        return '<meta http-equiv="refresh" content="0; url=/dashboard/">'
    return '<h1>NexaCRM</h1><p>Connect, manage, grow.</p><a href="/login">Login</a> <a href="/register">Create account</a>'

@app.get("/register", response_class=HTMLResponse)
def register_form() -> str:
    return '<h1>Create your NexaCRM account</h1><form method="post"><input name="full_name" placeholder="Full name" required><input name="username" placeholder="Username" required><input name="email" type="email" placeholder="Email" required><input name="password" type="password" placeholder="Password" required><button>Create account</button></form>'

@app.post("/register")
def register(full_name: Annotated[str, Form()], username: Annotated[str, Form()], email: Annotated[str, Form()], password: Annotated[str, Form()], db: Annotated[Session, Depends(get_db)]) -> RedirectResponse:
    if db.scalar(select(User).where((User.username == username) | (User.email == email))):
        raise HTTPException(status_code=409, detail="Username or email already registered")
    user = User(full_name=full_name.strip(), username=username.strip(), email=email.strip().lower(), password_hash=hash_password(password))
    db.add(user); db.commit()
    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_form() -> str:
    return '<h1>Log in to NexaCRM</h1><form method="post"><input name="identity" placeholder="Username or email" required><input name="password" type="password" placeholder="Password" required><button>Log in</button></form>'

@app.post("/login")
def login(identity: Annotated[str, Form()], password: Annotated[str, Form()], db: Annotated[Session, Depends(get_db)]) -> RedirectResponse:
    user = db.scalar(select(User).where((User.username == identity) | (User.email == identity.lower())))
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
    response = RedirectResponse("/dashboard/", status_code=303)
    response.set_cookie("access_token", token_for(user), httponly=True, secure=os.getenv("ENVIRONMENT") == "production", samesite="lax", max_age=604800)
    return response

@app.post("/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse("/login", status_code=303); response.delete_cookie("access_token"); return response

@app.get("/dashboard/", response_class=HTMLResponse)
def dashboard(request: Request, db: Annotated[Session, Depends(get_db)]) -> str:
    user = require_user(request, db)
    leads = db.scalar(select(func.count(Lead.id))) or 0
    students = db.scalar(select(func.count(Student.id))) or 0
    return f'<h1>NexaCRM dashboard</h1><p>Welcome, {user.full_name}</p><p>Leads: {leads} | Students: {students}</p><form method="post" action="/logout"><button>Log out</button></form>'

@app.get("/api/leads")
def list_leads(request: Request, db: Annotated[Session, Depends(get_db)]) -> list[dict]:
    require_user(request, db)
    return [
        {
            "id": lead.id,
            "name": lead.name,
            "phone": lead.phone,
            "email": lead.email,
            "course": lead.course,
            "source": lead.source,
            "status": lead.status,
            "priority": lead.priority,
            "notes": lead.notes,
            "assigned_to_id": lead.assigned_to_id,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
        }
        for lead in db.scalars(select(Lead).order_by(Lead.created_at.desc())).all()
    ]

class LeadCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr | None = None
    course: str = ""
    source: str = "Website"
    status: str = "New"
    priority: str = "Medium"
    notes: str = ""

@app.post("/api/leads", status_code=201)
def create_lead(payload: LeadCreate, request: Request, db: Annotated[Session, Depends(get_db)]) -> dict:
    user = require_user(request, db)
    lead = Lead(**payload.model_dump(exclude_none=True), assigned_to_id=user.id)
    db.add(lead); db.commit(); db.refresh(lead)
    return {"id": lead.id, "name": lead.name, "status": lead.status}
