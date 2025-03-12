import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://yourdomain.com",
    # Add more origins as needed
]

app = FastAPI(
        title="TEST API",
        description="Test API that writes and reads data to and from a JSON file",
        version = "1.0.0",
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

DATA_FILE = "data.json"  # JSON file for storage

# User Model
class User(BaseModel):
    id: int
    name: str
    email: str

# Load data from JSON file
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

# Save data to JSON file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Initialize data storage
users_db = load_data()

# Create a User
@app.post("/users/create_user/", response_model=User)
def create_user(user: User):
    if any(u["id"] == user.id for u in users_db):
        raise HTTPException(status_code=400, detail="User ID already exists.")
    
    users_db.append(user.dict())
    save_data(users_db)
    return user

# Get All Users
@app.get("/users/", response_model=List[User])
def get_users():
    return users_db

# Get a Single User by ID
@app.get("/users/get/{user_id}", response_model=User)
def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return User(**user)
    raise HTTPException(status_code=404, detail="User not found.")

# Update a User
@app.put("/users/update_user/{user_id}", response_model=User)
def update_user(user_id: int, updated_user: User):
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            users_db[index] = updated_user.dict()
            save_data(users_db)
            return updated_user
    raise HTTPException(status_code=404, detail="User not found.")

# Delete a User
@app.delete("/users/delete_user/{user_id}", response_model=User)
def delete_user(user_id: int):
    for index, user in enumerate(users_db):
        if user["id"] == user_id:
            deleted_user = users_db.pop(index)
            save_data(users_db)
            return User(**deleted_user)
    raise HTTPException(status_code=404, detail="User not found.")
