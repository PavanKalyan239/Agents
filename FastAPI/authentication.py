# authentication.py
# -----------------
# This module implements user authentication and authorization
# using FastAPI for the web framework,
# SQLAlchemy as the ORM for database interactions,
# Pydantic for data validation and serialization,
# PassLib for secure password hashing,
# and python-jose for JWT encoding/decoding.

# --- Imports ---
# HMAC for message authentication (currently unused, can be removed later if not needed)
from hmac import new
# FastAPI core classes and HTTP utilities
from fastapi import FastAPI, Depends, HTTPException, status
# OAuth2 helpers for password flow and dependency injection
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# SQLAlchemy ORM and types for database models and relationships
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
# Pydantic for request/response schema definitions and validations
from pydantic import BaseModel, EmailStr, Field, validator
# Literal type for role constraints and typing helpers
from typing import Literal, List, Optional, Annotated
# PassLib context for hashing and verifying passwords securely
from passlib.context import CryptContext  # type: ignore
# JOSE library components for JWT encoding/decoding and error handling
from jose import JWTError, jwt  # type: ignore
# Standard library for handling token expiry timestamps
import datetime

# --- Application & Database Setup ---
# Create FastAPI application instance
app = FastAPI()

# Use SQLite for demonstration; switch to PostgreSQL/MySQL in production
DATABASE_URL = "sqlite:///./test.db"
# SQLAlchemy engine with check_same_thread disabled for SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Base class for ORM models
Base = declarative_base()
# Session factory for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Security Configuration ---
# Secret key for signing JWT tokens (store securely in env vars in real apps)
SECRET_KEY = "mysecretkey"
# Algorithm used for JWT signature
ALGORITHM = "HS256"
# Token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context using bcrypt algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 scheme for extracting bearer tokens from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# --- ORM Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # Unique user ID
    username = Column(String, unique=True, index=True)  # User login name
    email = Column(String, unique=True, index=True)     # User email address
    hashed_password = Column(String)                    # Securely hashed password
    role = Column(String)                               # User role for access control
    # Relationship to Document model for back-population
    documents = relationship("Document", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)  # Document ID
    title = Column(String)                              # Document title
    content = Column(String)                            # Document body
    owner_id = Column(Integer, ForeignKey("users.id"))  # FK reference to owning user
    owner = relationship("User", back_populates="documents")  # ORM relationship

# Create database tables based on defined models
Base.metadata.create_all(bind=engine)

# --- Pydantic Schemas ---
class UserCreate(BaseModel):
    # Username must be between 3 and 50 characters
    username: Annotated[str, Field(min_length=3, max_length=50)]
    email: EmailStr                               # Validated email format
    # Password must be between 6 and 50 characters
    password: Annotated[str, Field(min_length=6, max_length=50)]
    role: Literal["admin", "editor", "user"] = "user"  # Role with default

    @validator('username')
    def username_length(cls, v: str) -> str:
        if not (3 <= len(v) <= 30):
            raise ValueError('username must be between 3 and 30 characters')
        return v

class Token(BaseModel):
    access_token: str  # JWT token string
    token_type: str    # e.g. "bearer"

class DocumentCreate(BaseModel):
    title: str    # Title for creating/updating documents
    content: str  # Content for creating/updating documents

class DocumentOut(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int

    class Config:
        from_attributes = True  # Enable ORM compatibility for response serialization

# --- Utility Functions & Dependencies ---

def get_db():
    """
    Dependency that provides a database session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str):
    """
    Hash a plaintext password using the configured PassLib context.
    """
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    """
    Verify a plaintext password against the stored hashed password.
    """
    return pwd_context.verify(plain, hashed)


def create_token(data: dict):
    """
    Generate a JWT token containing the provided data and expiration.
    """
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Dependency that decodes the JWT token, validates it, and retrieves
    the corresponding user from the database.
    Raises HTTPException if token is invalid or user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exception
    return user


def role_required(roles: List[str]):
    """
    Factory function returning a dependency that ensures the current user
    has one of the allowed roles; raises HTTPException if not.
    """
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden: insufficient role")
        return current_user
    return checker

# --- API Routes ---

@app.post("/register", response_model=Token)
# Register a new user; checks for duplicates, hashes password, saves user,
# and returns an access token.
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user.username) | (User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already registered")
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = create_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}   

@app.post("/login", response_model=Token)
# Authenticate user via OAuth2 form data and issue a JWT token.
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/documents", response_model=DocumentOut)
# Create a new document; only users with 'admin' or 'editor' roles allowed.
def create_doc(doc: DocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(role_required(["admin", "editor"]))):
    new_doc = Document(title=doc.title, content=doc.content, owner_id=current_user.id)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@app.get("/documents", response_model=List[DocumentOut])
# Retrieve all documents; permitted for 'admin', 'editor', and 'user' roles.
def read_all_docs(db: Session = Depends(get_db), current_user: User = Depends(role_required(["admin", "editor", "user"]))):
    return db.query(Document).all()

@app.put("/documents/{doc_id}", response_model=DocumentOut)
# Update an existing document; only 'admin' or the document owner can perform this.
def update_doc(doc_id: int, doc: DocumentCreate, db: Session = Depends(get_db), current_user: User = Depends(role_required(["admin", "editor"]))):
    existing_doc = db.query(Document).filter(Document.id == doc_id).first()
    if not existing_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if current_user.role != "admin" and existing_doc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can't edit this document")
    existing_doc.title = doc.title
    existing_doc.content = doc.content
    db.commit()
    db.refresh(existing_doc)
    return existing_doc

@app.delete("/documents/{doc_id}")
# Delete a document; restricted to 'admin' users.
def delete_doc(doc_id: int, db: Session = Depends(get_db), current_user: User = Depends(role_required(["admin"]))):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(doc)
    db.commit()
    return {"detail": "Deleted"}















