from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# import models here so SQLAlchemy knows about them
from app.db.models.merchant import Merchant # noqa

