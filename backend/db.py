import os
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.config import settings

client = AsyncIOMotorClient(settings.mongodb_uri)
db = client.strawberryDB
users_collection = db.users
predictions_collection = db.predictions

