# main.py
from fastapi import FastAPI, Depends, BackgroundTasks, Request, HTTPException, status, Header, UploadFile, File, Form, Cookie, WebSocket
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from enum import Enum
import time
import json
import logging
from pathlib import Path

app = FastAPI(
    title="FastAPI Structured Examples",
    description="Demonstrates core FastAPI features with unique endpoints and clear explanations.",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# -----------------------------------
# Section 1: Basic Endpoints
# -----------------------------------
# Concept: Introduces simple GET routes to return static messages and demonstrates path parameters.

@app.get("/", summary="Root Endpoint", tags=["Basics"])
def read_root():
    """Returns a welcome message."""
    return {"message": "Welcome to FastAPI!"}

@app.get("/hello/{name}", summary="Greet User", tags=["Basics"])
def greet_user(name: str):
    """Greets the user by name (path parameter)."""
    return {"message": f"Hello, {name}!"}

# -----------------------------------
# Section 2: Parameter Handling
# -----------------------------------
# Concept: Shows how to use query and path parameters to accept input from request URLs.

@app.get("/add", summary="Add Query Parameters", tags=["Parameters"])
def add_query(a: int = 0, b: int = 0):
    """Adds two integers passed as query parameters."""
    return {"result": a + b}

@app.get("/sum/{a}/{b}", summary="Sum Path Parameters", tags=["Parameters"])
def sum_path(a: int, b: int):
    """Adds two integers passed as path parameters."""
    return {"result": a + b}

# -----------------------------------
# Section 3: Request Body (Pydantic Model)
# -----------------------------------
# Concept: Leverages Pydantic BaseModel to validate and parse JSON payloads in POST requests.

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float

@app.post("/items/", summary="Create Item", tags=["Models"])
def create_item(item: Item):
    """Accepts an Item in the request body and returns it."""
    return item

# -----------------------------------
# Section 4: Response Model
# -----------------------------------
# Concept: Uses response_model to control output schema and hide internal fields.

class User(BaseModel):
    id: int
    name: str
    email: EmailStr

@app.get("/user", response_model=User, summary="Get Public User", tags=["Models"])
def get_user():
    """Returns a User model; other fields are hidden by response_model."""
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}

# -----------------------------------
# Section 5: Dependency Injection (Simple Token Auth)
# -----------------------------------
# Concept: Demonstrates header-based dependency injection for token authentication.

def verify_token(authorization: str | None = Header(None)):
    """Validates a simple token passed in the Authorization header or rejects missing token."""
    if not authorization or authorization != "TokenSecret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    return authorization

@app.get("/secure-data", summary="Secure Data", tags=["Auth"], dependencies=[Depends(verify_token)])
def secure_data():
    """Endpoint protected by a header-based token dependency."""
    return {"data": "This is protected data."}

# -----------------------------------
# Section 6: Background Tasks
# -----------------------------------
# Concept: Executes time-consuming tasks asynchronously after sending the response.

DB_FILE = Path("db/users.json")

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


def fake_hash(password: str) -> str:
    return "hashed_" + password


def save_user(user_dict: dict):
    """Writes user data to a JSON file."""
    users = []
    if DB_FILE.exists():
        users = json.loads(DB_FILE.read_text())
    users.append(user_dict)
    DB_FILE.write_text(json.dumps(users, indent=2))

@app.post("/register", summary="Register User", tags=["Tasks"])
def register(user: UserCreate, background_tasks: BackgroundTasks):
    """Saves user data with hashed password in a background task."""
    user_data = user.dict()
    user_data["password"] = fake_hash(user.password)
    background_tasks.add_task(save_user, user_data)
    return {"message": "Registration initiated."}

# -----------------------------------
# Section 7: Middleware Example
# -----------------------------------
# Concept: Shows how to write custom middleware to process requests and responses globally.

@app.middleware("http")
async def add_process_time(request: Request, call_next):  # noqa: ARG001
    """Adds X-Process-Time header to each response."""
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response

# -----------------------------------
# Section 8: Enum Constraint
# -----------------------------------
# Concept: Enforces fixed choices via Python Enum for path parameters.

class Category(str, Enum):
    book = "book"
    electronics = "electronics"
    clothing = "clothing"

@app.get("/category/{category}", summary="Get Category Info", tags=["Enums"])
def get_category(category: Category):
    """Demonstrates an Enum path parameter constraint."""
    return {"category": category, "info": f"Details for {category}."}

# -----------------------------------
# Section 9: Event Listeners
# -----------------------------------
# Concept: Hooks into application startup and shutdown events for initialization and cleanup.

fake_db: dict[str, list[str]] = {}

@app.on_event("startup")
async def startup_event():
    """Initialize fake database on application startup."""
    fake_db["users"] = ["Alice", "Bob"]

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup fake database on application shutdown."""
    fake_db.clear()

@app.get("/users", summary="List Users", tags=["Events"])
def list_users():
    """Returns users loaded during startup."""
    return {"users": fake_db.get("users", [])}

# -----------------------------------
# Section 10: File Uploads & Downloads
# -----------------------------------
# Concept: Handles file uploads with UploadFile and serves files with FileResponse, including 404 handling.

@app.post("/uploadfile", summary="Upload File", tags=["Files"])
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    logging.info(f"Received file {file.filename}, size={len(content)} bytes")
    return {"filename": file.filename, "size": len(content)}

@app.get("/download/{filename}", summary="Download File", tags=["Files"])
def download_file(filename: str):
    file_path = Path("static") / filename
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(path=file_path, filename=filename)

# -----------------------------------
# Section 11: Form Data & Cookies
# -----------------------------------
# Concept: Parses form fields and reads cookies from incoming requests.

@app.post("/login", summary="Form Login", tags=["Forms"])
def login(username: str = Form(...), password: str = Form(...), session_id: str | None = Cookie(None)):
    return {"username": username, "session_id": session_id}

# -----------------------------------
# Section 12: Custom Exception Handler
# -----------------------------------
# Concept: Defines and handles custom exceptions to return custom HTTP status codes and messages.

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(status_code=418, content={"message": f"Oops! {exc.name} did something."})

@app.get("/unicorns/{name}", summary="Unicorn Endpoint", tags=["Errors"])
def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}

# -----------------------------------
# Section 13: Streaming Responses
# -----------------------------------
# Concept: Streams large or infinite data gradually using StreamingResponse.

@app.get("/stream", summary="Streaming Response", tags=["Streaming"])
def stream_numbers():
    def generator():
        for i in range(10):
            yield f"number: {i}\n"
            time.sleep(0.1)
    return StreamingResponse(generator(), media_type="text/plain")

# -----------------------------------
# Section 14: WebSocket Support
# -----------------------------------
# Concept: Establishes a persistent bi-directional connection for real-time communication.

@app.websocket("/ws")  # summary and tags not supported for websocket routes
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

# -----------------------------------
# Section 15: Dependency with Teardown
# -----------------------------------
# Concept: Shows dependencies with setup and teardown logic using yield.

class DBSession:
    def __init__(self):
        self.connected = True
    def close(self):
        self.connected = False

async def get_db_session():
    session = DBSession()
    try:
        yield session
    finally:
        session.close()

@app.get("/items-db", summary="DB Dependency", tags=["Dependency"])
async def read_items_db(db: DBSession = Depends(get_db_session)):
    return {"db_connected": db.connected}

# -----------------------------------
# Section 16: Response Examples & Codes
# -----------------------------------
# Concept: Enriches OpenAPI docs with custom examples, multiple status codes, and descriptions.

@app.post(
    "/users-examples",
    response_model=User,
    status_code=201,
    summary="User with Examples",
    tags=["Models"],
    responses={
        201: {
            "description": "User created",
            "content": {
                "application/json": {
                    "example": {"id": 2, "name": "Bob", "email": "bob@example.com"}
                }
            }
        }
    }
)
def create_user_example(user: User):
    return user

