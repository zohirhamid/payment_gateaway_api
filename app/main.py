from fastapi import FastAPI

from app.api.routes.auth_debug import router as auth_debug_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

from sqlalchemy.orm import Session
from fastapi import Depends
from app.api.deps import get_db
from app.db.models.merchant import Merchant

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

# Create all tables for all registered models if they do not already exist
Base.metadata.create_all(bind=engine)
app.include_router(auth_debug_router)