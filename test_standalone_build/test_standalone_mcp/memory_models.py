import datetime
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field, ConfigDict

# --- Pydantic Models for API/Logic Layer ---

class InteractionRecordPydantic(BaseModel):
    id: Optional[int] = None # Will be set by DB
    session_id: Optional[str] = Field(None, description="Optional session identifier.")
    user_id: Optional[str] = Field(None, description="Optional user identifier.")
    query: str
    response: str
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    additional_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata.") # Renamed from metadata

    model_config = ConfigDict(from_attributes=True)


class InteractionRecordUpdatePydantic(BaseModel):
    """Pydantic model for updating an interaction record. All fields are optional."""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    query: Optional[str] = None
    response: Optional[str] = None
    # timestamp: Optional[datetime] = None # Usually, timestamp is not updated, but kept as original.
    additional_metadata: Optional[Dict[str, Any]] = None
    # No need for id or timestamp in an update model usually, or make timestamp explicitly updatable if needed.


# --- SQLAlchemy ORM Models ---

Base = declarative_base()

class InteractionRecordORM(Base):
    __tablename__ = "interaction_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, index=True, nullable=True)
    user_id = Column(String, index=True, nullable=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    additional_metadata = Column(JSON, nullable=True) # Renamed from 'metadata'

    def __repr__(self):
        return f"<InteractionRecordORM(id={self.id}, query='{self.query[:30]}...', response='{self.response[:30]}...')>"

# --- Database Utility Functions (can be expanded) ---

def create_db_engine_and_tables(db_url: str):
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session_local(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal
