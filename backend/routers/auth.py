from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.models.user import UserCreate, UserLogin, Token
from backend.core.security import verify_password, create_access_token
from backend.core.config import settings
from backend.db import users_collection
from typing import List

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/signup", response_model=dict)
async def signup(user: UserCreate):
    # Check unique email
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user.password = get_password_hash(user.password)
    
    # Insert user
    result = await users_collection.insert_one(user.dict())
    return {"message": "User created", "id": str(result.inserted_id)}

@router.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Find user
    user_doc = await users_collection.find_one({"email": form_data.username})
    if not user_doc or not verify_password(form_data.password, user_doc["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user_doc["_id"])}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"message": "Auth working"}

