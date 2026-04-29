from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from backend.routers import auth, ml
from backend.db import users_collection, predictions_collection

app = FastAPI(title="StrawberryGuard Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-netlify-site.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ml.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# @app.on_event("startup")
# async def startup():
    # # Test DB
    # await users_collection.database.command("ping")

@app.get("/")
async def root():
    return {"message": "StrawberryGuard FastAPI Backend Ready"}

