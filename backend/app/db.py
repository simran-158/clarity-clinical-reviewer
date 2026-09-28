from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


class Database:
    def __init__(self, url: str):
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        self.engine = create_engine(
            url,
            connect_args={"check_same_thread": False}
            if url.startswith("sqlite")
            else {},
            pool_pre_ping=True,
        )
        self.session = sessionmaker(self.engine, expire_on_commit=False)

    def create_tables(self):
        """Test setup only; application startup uses migrations."""
        Base.metadata.create_all(self.engine)
