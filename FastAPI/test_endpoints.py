# This File contains block by block execution of the FastAPI code.

#-------------------------------------------Basic FastAPI Example----------------------------------------------------#
# from fastapi import FastAPI

# application = FastAPI()


# @application.get("/")
# def read_root():
#     return {"Hello": "FastAPI"}

# @application.get("/hello/{name}")
# def read_item(name: str):
#     return {"Hello": name}

# uvicorn main:application --reload --port 8080

# uvicorn main:app --reload --port 8080

#-------------------------------------------Query Parameters and Path Parameters Example----------------------------------------------------#

# from fastapi import FastAPI
# from pydantic import BaseModel

# class Sum(BaseModel):
#     a: int
#     b: int

# app = FastAPI()

# @app.get("/greet/{name}")
# def greet(name: str):
#     return {"greeting": f"Hi {name}, welcome to FastAPI!!"}
# # curl -X GET "http://127.0.0.1:8080/greet/Kalyan" -H "accept: application/json"

# @app.post("/sum")
# def calculate_sum(sum: Sum):
#     result = sum.a + sum.b
#     return {"result": result}

# # curl -X POST "http://127.0.0.1:8080/sum" -H "Content-Type: application/json" -d "{\"a\": 2, \"b\": 3}"


# @app.get("/sum/{a}/{b}") # Path Parameters
# def calculate_sum(a: int, b: int):
#     result = a + b
#     return {"result": result}
# # curl -X GET "http://127.0.0.1:8080/sum/2/3" 


# @app.get("/add") # Query Parameters
# def calculate_add(a: int = 0, b: int = 0):
#     result = a + b
#     return {"result": result}

# # curl -X GET "http://127.0.0.1:8080/add?a=2&b=3"

# @app.get("/add/{a}") # Both Path and Query Parameters
# def calculate_add(a: int, b: int = 0):
#     result = a + b
#     return {"result": result}

# # curl -X GET "http://127.0.0.1:8080/add/2?b=3"


# class Comment(BaseModel):
#     user: str
#     text: str

# @app.post("/posts/{post_id}/comments") #Mix - All path, query and body parameters
# def add_comment(post_id: int, highlight: bool = False, comment: Comment = None):
#     return {
#         "post_id": post_id,
#         "highlight": highlight,
#         "comment_by": comment.user,
#         "comment": comment.text
#     }
# # curl -X POST "http://127.0.0.1:8080/posts/100/comments?highlight=True" -H "Content-Type: application/json" -d "{\"user\": \"Pavan\", \"text\": \"Nice\"}"

#--------------------------------------------Response Model Example----------------------------------------------------#

# from fastapi import FastAPI
# from pydantic import BaseModel

# app = FastAPI()

# class User(BaseModel):
#     id: int
#     name: str
#     email: str
#     age: int

# # response_model_include - Include only the specified fields in the response
# @app.get("/user", response_model=User, response_model_include={"name", "email"})
# def get_user():
#     return User(id=1, name="Alice", email="alice@example.com", age=30)
# # curl -X GET "http://127.0.0.1:8080/user/1"

# # response_model_exclude - Exclude the specified fields from the response
# @app.get("/user-public", response_model=User, response_model_exclude={"age"})
# def get_user():
#     return User(id=1, name="Alice", email="alice@example.com", age=30)

#---------------------------------------------Swagger/OpenAPI Customization Example----------------------------------------------------#

# from fastapi import FastAPI, Query
# from pydantic import BaseModel, Field

# app = FastAPI()

# class Item(BaseModel):
#     name: str = Field(..., title="Item Name", description="The name of the item", max_length=50, example="Laptop")
#     description: str = Field(None, title="Item Description", description="A brief description of the item", max_length=200, example="A high-performance laptop for gaming and work")
#     price: float = Field(..., gt=0, title="Item Price", description="The price of the item in USD", example=999.99)

# @app.post("/items/", summary="create new item...",
#           description="Create a new item with the specified name, description, and price.",
#           response_description="The created item details...",
#           )
# def create_item(item: Item):
#     return item

# # curl -X POST "http://127.0.0.1:8080/items/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\":\"Mobile\",\"description\":\"A high-performance Mobile for gaming and work\",\"price\":111.111}"

# @app.get("/search/", summary="Get items",
#            description="Get a list of items with optional filtering by name and price range.",
#            response_description="A list of items",
#           )
# def get_items(q: str = Query(..., title="Search Query", description="Search query to filter items by name", example="Laptop"), 
#               max_price: float = Query(None, title="Max Price", description="Maximum price to filter items", example=1000)):

#     return {"query": q, "max_price": max_price}
# # curl -X GET "http://127.0.0.1:8080/search/?q=Mobile&max_price=1212"

#----------------------------------------------Async FastAPI Example----------------------------------------------------#

# from fastapi import FastAPI
# import time
# import asyncio

# app = FastAPI()

# @app.get("/api/1")
# async def method_1():
#     print("Method 1")
#     time.sleep(5)
#     print("Method 1 done")
#     return {"message": "Method 1"}
# # This will be running in the Synchronous context, so it will block the event loop.
# # It will not allow other requests to be processed until this method is completed.
# # This will not create any thread in the background and will block the main thread.

# @app.get("/api/2")
# async def method_2():
#     print("Method 2")
#     await asyncio.sleep(5)
#     print("Method 2 done")
#     return {"message": "Method 2"}
# # This will be running in the Asynchronous context, so it will not block the event loop.
# # It will allow other requests to be processed while this method is waiting for the sleep to complete.
# # This will create a new thread in the background and will not block the main thread.

# @app.get("/api/3")
# def method_3():
#     print("Method 3")
#     time.sleep(5)
#     print("Method 3 done")
#     return {"message": "Method 3"}
# # This will be running in the Asynchronous context, so it will not block the event loop.
# # This will create the seperate process in the background and will not block the main thread.

# curl -X GET http://127.0.0.1:8080/api/1

# uvicorn intro:app --reload --port 8080



#----------------------------------------------FastAPI Enum Constraint Example----------------------------------------------------#

# from fastapi import FastAPI, status
# from enum import Enum
# from pydantic import BaseModel, EmailStr

# app = FastAPI()

# class ItemType(str, Enum):
#     book = "book"
#     electronics = "electronics"
#     clothing = "clothing"
#     food = "food"

# @app.get("/items/{item}", summary="Get item details",
#           description="Get details of a specific item by its type.",
#           response_description="Details of the requested item",)
# def read_item(item: ItemType):
#     items= {
#         "book": {"name": "The Great Gatsby", "price": 10.99},
#         "electronics": {"name": "Smartphone", "price": 699.99},
#         "clothing": {"name": "T-shirt", "price": 19.99},
#         "food": {"name": "Pizza", "price": 12.99}
#     }
#     return {"item_id": item, "item_details": items[item]}
# # # curl -X GET "http://127.0.0.1:8080/items/book"


# # Input Model
# class UserCreate(BaseModel):
#     name: str
#     age: int
#     email: EmailStr
#     password: str

# # Output Model
# class UserPublic(BaseModel):
#     name: str
#     age: int
#     email: EmailStr

# # Route to create a new user
# @app.post("/users/", response_model=UserPublic, summary="Create a new user",
#             description="Create a new user with the specified name, age, email, and password.",
#             response_description="The created user's public details", status_code=status.HTTP_201_CREATED)
# def create_user(user: UserCreate):
#     return UserPublic(name=user.name, age=user.age, email=user.email)

# # curl -X POST "http://127.0.0.1:8080/users/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\":\"John Doe\",\"age\":30,\"email\":\"johndoe@gamil.com\",\"password\":\"password123\"}"



#----------------------------------------------Hash Password and Save details to JSON file Example----------------------------------------------------#
# from fastapi import FastAPI, status, HTTPException
# from pydantic import BaseModel, EmailStr
# from enum import Enum
# from pathlib import Path
# import json

# DB_FILE = Path("db/users.json")

# app = FastAPI()

# # Models
# class UserCreate(BaseModel):
#     name: str
#     age: int
#     email: EmailStr
#     password: str


# class UserPublic(BaseModel):
#     name: str
#     age: int
#     email: EmailStr

# # fake hash password
# def fake_hash_password(password: str):
#     return "fakehashed" + password

# def read_users_from_db():
#     if not DB_FILE.exists():
#         return []
#     with DB_FILE.open("r", encoding="utf-8") as f:
#         try:
#             return json.load(f)
#         except json.JSONDecodeError:
#             return []

# def write_users_to_db(users_dict):
#     users = read_users_from_db()
#     users.append(users_dict)
#     with DB_FILE.open("w", encoding="utf-8") as f:
#         json.dump(users, f, ensure_ascii=False, indent=4)


# # Routes
# @app.post("/users/", response_model=UserPublic, summary="Create a new user",
#             description="Create a new user with the specified name, age, email, and password.",
#             response_description="The created user's public details", status_code=status.HTTP_201_CREATED)
# def create_user(user: UserCreate):
#     # Check if user already exists
#     users = read_users_from_db()
#     for existing_user in users:
#         if existing_user["email"] == user.email:
#             raise HTTPException(status_code=400, detail="Email already registered")

#     # Hash password and save user to DB
#     hashed_password = fake_hash_password(user.password)
#     user_dict = user.model_dump()
#     user_dict["password"] = hashed_password
#     write_users_to_db(user_dict)

#     return UserPublic(name=user.name, age=user.age, email=user.email)

# # curl -X POST "http://127.0.0.1:8080/users/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\":\"John Doe\",\"age\":30,\"email\":\"johndoe@gmail.com\",\"password\":\"password123\"}"


#-----------------------------------------------Custom Validation Example----------------------------------------------------#

# from fastapi import FastAPI, status, HTTPException
# from pydantic import BaseModel, EmailStr, Field, field_validator, constr
# import re

# app = FastAPI()

# class UserCreate(BaseModel):
#     name: str = Field(..., min_length=3, max_length=50)
#     age: int = Field(..., ge=0, le=120)
#     email: EmailStr
#     password: str= Field(..., min_length=8)

#     @field_validator("password")
#     def validate_password(cls, value):
#         if not re.search(r"[A-Z]", value):
#             raise ValueError("Password must contain at least one uppercase letter")
#         if not re.search(r"[a-z]", value):
#             raise ValueError("Password must contain at least one lowercase letter")
#         if not re.search(r"[0-9]", value):
#             raise ValueError("Password must contain at least one digit")
#         if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
#             raise ValueError("Password must contain at least one special character")
#         return value

#     @field_validator("name")
#     def validate_name(cls, value):
#         if not re.match(r"^[A-Za-z\s]+$", value):
#             raise ValueError("Name must contain only letters and spaces")
#         return value
    
# class UserPublic(BaseModel):
#     name: str
#     age: int
#     email: EmailStr

# @app.post("/users/", summary="Create a new user",
#         description="Create a new user with the specified name, age, email, and password.",
#         response_description="The created user's public details", response_model=UserPublic , status_code=status.HTTP_201_CREATED)
# def create_user(user: UserCreate):
#     return UserPublic(name=user.name, age=user.age, email=user.email)

# # curl -X POST "http://127.0.0.1:8080/users/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\":\"John Doe\",\"age\":30,\"email\":\"user@gmail.com\",\"password\":\"Password123!\"}"

#------------------------------------------------Dependency Injection Example----------------------------------------------------#

# from fastapi import FastAPI, Depends, HTTPException, status, Header

# app = FastAPI()

# # # Fake token check (can replace with real logic later)
# def fake_token_validator(authorization: str = Header(default="")):
#     print("Token:", authorization)
#     if authorization != "secrettoken123":
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or missing token",
#         )
#     return authorization

# @app.get("/secure-data/", dependencies=[Depends(fake_token_validator)])
# def get_secure_data():
#     return {"message": "This is secure data"}

# # curl -X GET "http://127.0.0.1:8080/secure-data/" -H "accept: application/json" -H "Authorization: secrettoken123"


#------------------------------------------------Background Tasks Example----------------------------------------------------#

# from fastapi import FastAPI, BackgroundTasks, Query
# from pydantic import EmailStr, BaseModel
# app = FastAPI()

# class User(BaseModel):
#     email: EmailStr

# def send_background_email(email: str, message: str):
#     # Simulate sending an email
#     print(f"Sending email to {email} with message: {message}")

# @app.post("/register/", summary="Register a new user",
#             description="Register a new user and send a welcome email in the background.",
#             response_description="Registration successful message")
# def register_user(user: User, background_tasks: BackgroundTasks):
#     message = "Welcome to our service!"
#     background_tasks.add_task(send_background_email, user.email, message)
#     return {"message": "User registered successfully!"}

# # curl -X POST "http://127.0.0.1:8080/register/" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"email\":\"sample@example.com\"}"

# @app.post("/registerq/", summary="Register a new user",
#             description="Register a new user and send a welcome email in the background.",
#             response_description="Registration successful message")
# def register_user( background_tasks: BackgroundTasks, email: EmailStr = Query(..., title="User Email", description="Email address of the user to register", example="hello@gmail.com")):
#     message = "Welcome to our service!"
#     background_tasks.add_task(send_background_email, email, message)
#     return {"message": "User registered successfully!"}

# # curl -X POST "http://127.0.0.1:8080/registerq/?email=hello@gamil.com" 

#------------------------------------------------Middleware Example----------------------------------------------------#
# from fastapi import FastAPI, Request
# import time

# app= FastAPI()

# @app.middleware("http")
# async def log_request_time(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     print(f"Request: {request.method} {request.url} - Process Time: {process_time:.4f} seconds")
#     return response

# @app.get("/")
# def read_root():
#     return {"message": "Hello, World!"}

# # curl -X GET "http://127.0.0.1:8080/"

#------------------------------------------------Routers-Middleware-Depends Example----------------------------------------------------#

# from fastapi import FastAPI, Depends, HTTPException, status, Request
# from fastapi.routing import APIRouter
# from fastapi.responses import JSONResponse
# from jose import JWTError, jwt
# from pydantic import BaseModel
# from starlette.middleware.base import BaseHTTPMiddleware
# from typing import List, Optional
# from datetime import datetime, timedelta

#     # ---------------------- CONFIG ----------------------

# SECRET_KEY = "ImASecretKey"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# fake_users_db = {
#     "admin": {"username": "admin", "roles": ["admin"], "disabled": False},
#     "alice": {"username": "alice", "roles": ["user"], "disabled": False},
# }

#     # ---------------------- MODELS ----------------------

# class User(BaseModel):
#     username: str
#     roles: List[str]
#     disabled: bool = False

# class TokenData(BaseModel):
#     sub: Optional[str] = None

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class Users(BaseModel):
#     username: str
#     password: str

#     # ---------------------- SECURITY ----------------------

# def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + expires_delta
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#     # ---------------------- MIDDLEWARE ----------------------

# class JWTMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         token = request.headers.get("Authorization")
#         if token and token.startswith("Bearer "):
#             try:
#                 payload = jwt.decode(token[7:], SECRET_KEY, algorithms=[ALGORITHM])
#                 print(f"----------------JWTMiddleware- payload : {payload}-----------------")
#                 request.state.user_id = payload.get("sub")
#             except JWTError:
#                 pass  # Token errors handled later
#                 print(f"----------------JWTMiddleware- JWTError : {JWTError}-----------------")
#         else:
#             print(f"----------------JWTMiddleware- No token found-----------------")
#         return await call_next(request)
    
#     # ---------------------- DEPENDENCIES ----------------------

# async def get_current_user(request: Request) -> User:
#     print(f"----------------get_current_user- request.state : {request.state.__dict__}-----------------")
#     print(f"----------------get_current_user- request.headers : {request.headers}-----------------")
#     user_id = getattr(request.state, "user_id", None)
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Not authenticated")
    
#     user_data = fake_users_db.get(user_id)
#     if not user_data:
#         raise HTTPException(status_code=404, detail="User not found")

#     return User(**user_data)

# def require_role(role: str):
#     def role_checker(user: User = Depends(get_current_user)):
#         if role not in user.roles:
#             raise HTTPException(status_code=403, detail="Forbidden")
#         return user
#     return role_checker

#     # ---------------------- ROUTERS ----------------------

# user_router = APIRouter()
# admin_router = APIRouter()
# auth_router = APIRouter()

# @auth_router.post("/token", response_model=Token)
# async def login(users:Users):
#     # No password checking here for simplicity
#     username = users.username
#     password = users.password
#     print(f"----------------login- username : {username}-----------------")
#     print(f"----------------login- password : {password}-----------------")
#     if username not in fake_users_db:
#         raise HTTPException(status_code=400, detail="Invalid credentials")

#     access_token = create_access_token(data={"sub": username})
#     return {"access_token": access_token, "token_type": "bearer"}
# # curl -X POST http://127.0.0.1:8000/token -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"yourpassword\"}"
# # we are not validating any passwprd here, just for simplicity

# @user_router.get("/users/me")
# async def read_me(user: User = Depends(get_current_user)):
#     return user
# # curl -X GET http://127.0.0.1:8000/users/me -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0Njg5NDIwOH0.lyzBVpb44Z3eCBC7f0LoRlk2pRJMMJWGPK39cuVyyoI"
# # sample response: {"username":"admin","roles":["admin"],"disabled":false}

# @admin_router.get("/admin-only")
# async def admin_only(user: User = Depends(require_role("admin"))):
#     return {"msg": f"Hello Admin {user.username}"}
# # curl -X GET http://127.0.0.1:8000/admin-only -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0Njg5NDIwOH0.lyzBVpb44Z3eCBC7f0LoRlk2pRJMMJWGPK39cuVyyoI"
# # sample response: {"msg":"Hello Admin admin"}
#     # ---------------------- APP INIT ----------------------

# app = FastAPI()
# app.add_middleware(JWTMiddleware)
# app.include_router(auth_router)
# app.include_router(user_router)
# app.include_router(admin_router)

#-----------------------------------------------Event Listeners----------------------------------------------------#

# from fastapi import FastAPI

# app = FastAPI()
# fake_db = {}

# @app.on_event("startup")
# async def load_data():
#     print("Startup: loading users...")
#     fake_db["users"] = ["Alice", "Bob"]

# @app.on_event("shutdown")
# async def cleanup_data():
#     print("Shutdown: cleaning up users...")
#     fake_db.clear()

# @app.get("/users/")
# def get_users():
#     return {"users": fake_db.get("users", [])}

#---------------------------------------------Authentication and Authorization Example----------------------------------------------------#

# from fastapi import FastAPI, Depends, HTTPException, status, Request
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from jose import JWTError, jwt
# from pydantic import BaseModel
# from datetime import datetime, timedelta


# app = FastAPI()

# SECRET_KEY = "ImASecretKey"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# fake_users_db = {
#     "admin": {
#         "username": "admin",
#         "password": "yourpassword",
#         "full_name": "Admin User",
#         "email": "admin@example.com",
#     }
# }

# oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# def authenticate_user(username: str, password: str):
#     user = fake_users_db.get(username)
#     if not user or password != user.get("password"):
#         return  None
#     return user

# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# def get_current_user(token: str = Depends(oauth2scheme)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise HTTPException(status_code=401, detail="Invalid Authentication Credentials")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Unable to decode the Credentials")
#     return {"username": username}

# @app.post("/token", response_model=Token)
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)

#     if  not user:
#         raise HTTPException(status_code=401, detail="Invalid Authentication Credentials")
#     access_token = create_access_token(data={"sub": user["username"]})
#     return {"access_token": access_token, "token_type": "bearer"}
# # curl -X POST "http://127.0.0.1:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=yourpassword"
# # {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0Njk0OTkxM30.XHWUHogUwyQ9RMcIfujYpTBmp0kFgqh1MKR9q-GBEr4","token_type":"bearer"}


# @app.get("/users/me")
# def read_users_me(current_user: dict = Depends(get_current_user)):
#     return "Hello, " + current_user["username"] + "!"
# # curl -X GET "http://127.0.0.1:8000/users/me" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0Njk0OTkxM30.XHWUHogUwyQ9RMcIfujYpTBmp0kFgqh1MKR9q-GBEr4"


#------------------------------------------------Authentication------------------------------------------#

# from fastapi import Depends, FastAPI, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from passlib.context import CryptContext
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from typing import Optional
# from pydantic import BaseModel


# # ========== CONFIURATIONS ==========
# SECRET_KEY = "KALYAN"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # ========== PASSWORD HASHING ==========
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # ========== FAKE DATABASE ==========
# fake_users_db = {
#     "alice": {
#         "username": "alice",
#         "full_name": "Alice Wonderson",
#         "hashed_password": pwd_context.hash("secret"),
#         "disabled": False,
#         "roles": ["user"]
#     },
#     "admin": {
#         "username": "admin",
#         "full_name": "Admin User",
#         "hashed_password": pwd_context.hash("adminpass"),
#         "disabled": False,
#         "roles": ["admin", "user"]
#     }
# }

# # ========== Pydantics Data Models ==========

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: Optional[str] = None

# class User(BaseModel):
#     username: str
#     full_name: str
#     disabled: Optional[bool] = None
#     roles: list[str] = []

# class UserInDB(User):
#     hashed_password: str

# # ========== FastAPI APP ==========
# app = FastAPI()
# oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")

# # ========== UTILITY FUNCTIONS ==========

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_user(username: str):
#     user = fake_users_db.get(username)
#     if user:
#         print(f"----------------get_user : {UserInDB(**user)}-----------------")
#         return UserInDB(**user)

# def authenticate_user(username: str, password: str):
#     user = get_user(username)
#     if not user or not verify_password(password, user.hashed_password):
#         return False
#     print(f"----------------authenticate_user : {user}-----------------")
#     return user

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     print(f"----------------create_access_token : {encoded_jwt}-----------------")
#     return encoded_jwt
    

# # ========== DEPENDENCIES ==========

# async def get_current_user(token: str = Depends(oauth2scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"}
#     )
#     try:
#         print(f"----------------get_current_user : {token}-----------------")
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         print(f"----------------get_current_user payload : {payload}-----------------")
#         username: str = payload.get("sub")
#         if not username:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = get_user(token_data.username)
#     if not user:
#         raise credentials_exception
#     return user

# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

# def require_role(role: str):
#     print(f"----------------require_role : {role}-----------------")
#     def role_checker(user: User = Depends(get_current_active_user)):
#         if role not in user.roles:
#             raise HTTPException(status_code=403, detail="Not enough permissions")
#         return user
#     return role_checker

# # ========== ROUTES ==========

# @app.post("/token", response_model=Token)
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Incorrect username or password")
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}
# # curl -X POST http://127.0.0.1:8000/token -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=adminpass"
# # sample response: {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0NjQ5OTM4Nn0.LHK-AgB4Vf8eKk_8ttYewgt7cvwu4Ku9bwFJxKlUKCM","token_type":"bearer"}


# @app.get("/users/me/", response_model=User) # Notice the trailing slash
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     print(f"----------------2. read_users_me : {current_user}-----------------")
#     return current_user
# # curl -X GET http://127.0.0.1:8000/users/me/ -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0NjQ5OTM4Nn0.LHK-AgB4Vf8eKk_8ttYewgt7cvwu4Ku9bwFJxKlUKCM"


# @app.get("/admin-only")
# async def admin_endpoint(current_user: User = Depends(require_role("admin"))):
#     print(f"----------------3. admin_endpoint : {current_user}-----------------")
#     return {"message": f"Welcome Admin!, {current_user.username}"}
# # Non-Admin User: {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTc0NjUwMDA5Nn0.yOzGRyCxmKUvN36xt3tG5HUmVYza1OR0Db4wqKB4w1Q","token_type":"bearer"}
# # curl -X GET http://127.0.0.1:8000/admin-only/ -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTc0NjUwMDA5Nn0.yOzGRyCxmKUvN36xt3tG5HUmVYza1OR0Db4wqKB4w1Q"




# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # 👇 Allowed origins - only these origins can access your API
# origins = [
#     "http://127.0.0.1:3000",  # React dev server
#     "https://yourdomain.com",  # Production frontend
# ]

# # 👇 Register the CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,              # Who is allowed
#     allow_credentials=True,             # Allow cookies/auth headers
#     allow_methods=["*"],                # Which HTTP methods
#     allow_headers=["*"],                # Which headers
# )

# @app.get("/")
# def read_root():
#     return {"message": "Hello from API with CORS!"}

#-------------------------------------------------------- Testing with Pytest -----------------------------------------------# 
# from fastapi.testclient import TestClient
# from main import app

# client = TestClient(app)

# def test_create_user_success():
#     response = client.post(
#         "/users/",
#         json={"name": "Alice", "email": "alice@example.com", "age": 25}
#     )
#     assert response.status_code == 200
#     assert response.json() == {
#         "name": "Alice",
#         "email": "alice@example.com",
#         "age": 25
#     }

# def test_create_user_invalid_email():
#     response = client.post(
#         "/users/",
#         json={"name": "Bob", "email": "not-an-email", "age": 30}
#     )
#     assert response.status_code == 422  # Unprocessable Entity

# def test_create_user_missing_field():
#     response = client.post(
#         "/users/",
#         json={"name": "Charlie", "email": "charlie@example.com"}  # missing age
#     )
#     assert response.status_code == 422

#---------------------------------------------Upload File-------------------------------------#

# Upload a Single File
# from fastapi import FastAPI, File, UploadFile
# from fastapi.responses import JSONResponse

# app = FastAPI()

# @app.post("/uploadfile/")
# async def upload_file(file: UploadFile = File(...)):
#     contents = await file.read()  # ⚠️ Reads entire file into memory
#     return {
#         "filename": file.filename,
#         "content_type": file.content_type,
#         "size": len(contents)
#     }

# curl -X POST http://127.0.0.1:8000/uploadfile/ -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@setup.txt"

# @app.post("/uploadfile/save")
# async def upload_file(file: UploadFile = File(...)):
#     file_location = f"{file.filename}"
#     with open(file_location, "wb") as f:
#         content = await file.read()
#         f.write(content)
#     return {"info": f"File saved at {file_location}"}

# curl -X POST http://127.0.0.1:8000/uploadfile/save -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@setup.txt"

from typing import List

# @app.post("/uploadfiles/")
# async def upload_multiple_files(files: List[UploadFile] = File(...)):
#     return {
#         "filenames": [file.filename for file in files]
#     }

# @app.post("/uploadfiles/")
# async def upload_multiple_files(files: List[UploadFile] = File(...)):
#     saved_files = []
#     for file in files:
#         file_location = file.filename
#         with open(file_location, "wb") as f:
#             content = await file.read()  # Read file content
#             f.write(content)            # Save to disk
#         saved_files.append(file.filename)

#     return {"saved_files": saved_files}

# curl -X POST "http://127.0.0.1:8000/uploadfiles/" H "accept: application/json" -H "Content-Type: multipart/form-data" -F "files=@setupp.txt"

#---------------------------------------------File Serving------------------------------------------#

# from fastapi import FastAPI
# from fastapi.responses import FileResponse

# app = FastAPI()

# @app.get("/download/")
# def download_file():
#     return FileResponse("index.html", media_type="text/html", filename="report.html")

# curl -O http://127.0.0.1:8000/download/
# curl -OJ http://127.0.0.1:8000/download/

#------------------------------------------Streaming Response-----------------------------------------------#

# from fastapi import FastAPI
# from fastapi.responses import StreamingResponse
# import time

# app = FastAPI()

# def generate_logs():
#     for i in range(10):
#         yield f"Log line {i}\n"
#         time.sleep(1)  # Simulate a delay

# @app.get("/stream-logs/")
# def get_logs():
#     return StreamingResponse(generate_logs(), media_type="text/plain")
# # curl http://127.0.0.1:8000/stream-logs/

#------------------------------------------WebSocket Example-----------------------------------------------#
# from fastapi import FastAPI, WebSocket
# from fastapi.responses import HTMLResponse

# app = FastAPI()

# @app.get("/")
# async def get():
#     return HTMLResponse("""
#         <html>
#             <body>
#                 <h2>WebSocket Test</h2>
#                 <button onclick="connectWS()">Connect</button>
#                 <input id="messageInput" />
#                 <button onclick="sendMessage()">Send</button>
#                 <ul id="messages"></ul>
#                 <script>
#                     let ws;
#                     function connectWS() {
#                         ws = new WebSocket("ws://localhost:8000/ws");
#                         ws.onmessage = function(event) {
#                             const messages = document.getElementById("messages");
#                             const li = document.createElement("li");
#                             li.textContent = "Server: " + event.data;
#                             messages.appendChild(li);
#                         };
#                     }
#                     function sendMessage() {
#                         const input = document.getElementById("messageInput");
#                         ws.send(input.value);
#                     }
#                 </script>
#             </body>
#         </html>
#     """)

# @app.websocket("/ws")
# async def websocket_endpoint(websoc: WebSocket):
#     await websoc.accept()
#     while True:
#         data = await websoc.receive_text()
#         await websoc.send_text(f"Message text was: {data}")

# curl -X GET http://127.0.0.1:8000/





#----------------------------------Authentication -------------------------------------------#
# from fastapi import Depends, FastAPI, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from passlib.context import CryptContext
# from jose import JWTError, jwt
# from datetime import datetime, timedelta
# from typing import Optional
# from pydantic import BaseModel


# # ========== CONFIURATIONS ==========
# SECRET_KEY = "KALYAN"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # ========== PASSWORD HASHING ==========
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # ========== FAKE DATABASE ==========
# fake_users_db = {
#     "alice": {
#         "username": "alice",
#         "full_name": "Alice Wonderson",
#         "hashed_password": pwd_context.hash("secret"),
#         "disabled": False,
#         "roles": ["user"]
#     },
#     "admin": {
#         "username": "admin",
#         "full_name": "Admin User",
#         "hashed_password": pwd_context.hash("adminpass"),
#         "disabled": False,
#         "roles": ["admin", "user"]
#     }
# }

# # ========== Pydantics Data Models ==========

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: Optional[str] = None

# class User(BaseModel):
#     username: str
#     full_name: str
#     disabled: Optional[bool] = None
#     roles: list[str] = []

# class UserInDB(User):
#     hashed_password: str

# # ========== FastAPI APP ==========
# app = FastAPI()
# oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")

# # ========== UTILITY FUNCTIONS ==========

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_user(username: str):
#     user = fake_users_db.get(username)
#     if user:
#         print(f"----------------get_user : {UserInDB(**user)}-----------------")
#         return UserInDB(**user)

# def authenticate_user(username: str, password: str):
#     user = get_user(username)
#     if not user or not verify_password(password, user.hashed_password):
#         return False
#     print(f"----------------authenticate_user : {user}-----------------")
#     return user

# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     print(f"----------------create_access_token : {encoded_jwt}-----------------")
#     return encoded_jwt
    

# # ========== DEPENDENCIES ==========

# async def get_current_user(token: str = Depends(oauth2scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"}
#     )
#     try:
#         print(f"----------------get_current_user : {token}-----------------")
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         print(f"----------------get_current_user payload : {payload}-----------------")
#         username: str = payload.get("sub")
#         if not username:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#     except JWTError:
#         raise credentials_exception
#     user = get_user(token_data.username)
#     if not user:
#         raise credentials_exception
#     return user

# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user

# def require_role(role: str):
#     print(f"----------------require_role : {role}-----------------")
#     def role_checker(user: User = Depends(get_current_active_user)):
#         if role not in user.roles:
#             raise HTTPException(status_code=403, detail="Not enough permissions")
#         return user
#     return role_checker

# # ========== ROUTES ==========

# @app.post("/token", response_model=Token)
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Incorrect username or password")
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}
# # curl -X POST http://127.0.0.1:8000/token -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=adminpass"
# # sample response: {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0NjQ5OTM4Nn0.LHK-AgB4Vf8eKk_8ttYewgt7cvwu4Ku9bwFJxKlUKCM","token_type":"bearer"}


# @app.get("/users/me/", response_model=User) # Notice the trailing slash
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     print(f"----------------2. read_users_me : {current_user}-----------------")
#     return current_user
# # curl -X GET http://127.0.0.1:8000/users/me/ -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc0NjQ5OTM4Nn0.LHK-AgB4Vf8eKk_8ttYewgt7cvwu4Ku9bwFJxKlUKCM"


# @app.get("/admin-only")
# async def admin_endpoint(current_user: User = Depends(require_role("admin"))):
#     print(f"----------------3. admin_endpoint : {current_user}-----------------")
#     return {"message": f"Welcome Admin!, {current_user.username}"}
# # Non-Admin User: {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTc0NjUwMDA5Nn0.yOzGRyCxmKUvN36xt3tG5HUmVYza1OR0Db4wqKB4w1Q","token_type":"bearer"}
# # curl -X GET http://127.0.0.1:8000/admin-only/ -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSIsImV4cCI6MTc0NjUwMDA5Nn0.yOzGRyCxmKUvN36xt3tG5HUmVYza1OR0Db4wqKB4w1Q"

# # Testing
# import requests

# BASE_URL = "http://127.0.0.1:8000"

# def test_login(username, password):
#     response = requests.post(
#         f"{BASE_URL}/token",
#         data={"username": username, "password": password},
#         headers={"Content-Type": "application/x-www-form-urlencoded"}
#     )
#     print(f"Login Test ({username}, {password}): {response.status_code}, {response.json()}")
#     return response.json().get("access_token") if response.status_code == 200 else None

# def test_get_user_me(token):
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.get(f"{BASE_URL}/users/me/", headers=headers)
#     print(f"Get User Me Test: {response.status_code}, {response.json()}")

# def test_admin_only(token):
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.get(f"{BASE_URL}/admin-only", headers=headers)
#     print(f"Admin Only Test: {response.status_code}, {response.json()}")

# def test_token_expiry(expired_token):
#     headers = {"Authorization": f"Bearer {expired_token}"}
#     response = requests.get(f"{BASE_URL}/users/me/", headers=headers)
#     print(f"Token Expiry Test: {response.status_code}, {response.json()}")

# def test_invalid_token_format():
#     headers = {"Authorization": "Bearer invalid_token_format"}
#     response = requests.get(f"{BASE_URL}/users/me/", headers=headers)
#     print(f"Invalid Token Format Test: {response.status_code}, {response.json()}")

# def test_edge_cases_login():
#     edge_cases = [
#         {"username": "", "password": ""},  # Empty credentials
#         {"username": "a" * 256, "password": "b" * 256},  # Extremely long credentials
#         {"username": "user!@#", "password": "pass!@#"}  # Special characters
#     ]
#     for case in edge_cases:
#         response = requests.post(
#             f"{BASE_URL}/token",
#             data={"username": case["username"], "password": case["password"]},
#             headers={"Content-Type": "application/x-www-form-urlencoded"}
#         )
#         print(f"Edge Case Login Test ({case['username']}, {case['password']}): {response.status_code}, {response.json()}")

# def test_rate_limiting():
#     for _ in range(10):  # Simulate multiple requests
#         response = requests.get(f"{BASE_URL}/users/me/")
#         print(f"Rate Limiting Test: {response.status_code}, {response.json()}")

# def main():
#     # Test cases
#     print("=== Testing Login ===")
#     admin_token = test_login("admin", "adminpass")  # Valid admin credentials
#     user_token = test_login("alice", "secret")      # Valid user credentials
#     invalid_token = test_login("invalid", "wrong")  # Invalid credentials

#     print("\n=== Testing /users/me/ ===")
#     if admin_token:
#         test_get_user_me(admin_token)  # Admin user
#     if user_token:
#         test_get_user_me(user_token)  # Regular user
#     if invalid_token:
#         test_get_user_me(invalid_token)  # Invalid token (should fail)

#     print("\n=== Testing /admin-only ===")
#     if admin_token:
#         test_admin_only(admin_token)  # Admin user (should pass)
#     if user_token:
#         test_admin_only(user_token)  # Regular user (should fail)

#     print("\n=== Testing Token Expiry ===")
#     expired_token = "expired_token_example"  # Replace with an actual expired token if available
#     test_token_expiry(expired_token)

#     print("\n=== Testing Invalid Token Format ===")
#     test_invalid_token_format()

#     print("\n=== Testing Edge Cases for Login ===")
#     test_edge_cases_login()

#     print("\n=== Testing Rate Limiting ===")
#     test_rate_limiting()

# if __name__ == "__main__":
#     main()

#----------------------------------------



