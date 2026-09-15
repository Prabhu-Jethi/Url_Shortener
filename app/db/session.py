from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

## creating sql alchemy engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


## Add a database dependency, helps fastapi to inject a db session into routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()