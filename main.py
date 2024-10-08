from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User
import redis
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Define a Pydantic model for user creation
class UserCreate(BaseModel):
    name: str

# Define the App settings and configurations within a class
class AppConfig:
    DATABASE_URL: str = "sqlite:///./db/test.db"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

# Database Handler Class
class Database:
    def __init__(self, database_url: str) -> None:
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)  # Create tables

    def get_db(self) -> Session:
        """Dependency to retrieve database session."""
        db: Session = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Redis Cache Handler Class
class RedisCache:
    def __init__(self, host: str, port: int) -> None:
        self.redis_client = redis.StrictRedis(host=host, port=port, db=0)

    async def set(self, key: str, value: str) -> None:
        await self.redis_client.set(key, value)

    def get(self, key: str) -> Optional[str]:
        cached_value: bytes | None = self.redis_client.get(key)
        if cached_value:
            return cached_value.decode('utf-8')
        return None

# FastAPI app instance
app = FastAPI(root_path="/api")  # Same as nginx location

# Initialize the Database and Redis cache
db_handler = Database(AppConfig.DATABASE_URL)
redis_handler = RedisCache(AppConfig.REDIS_HOST, AppConfig.REDIS_PORT)

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint returning a simple message."""
    return {"message": "Hello World"}

@app.get("/hello/{name}", response_model=Dict[str, str])
async def say_hello(name: str) -> Dict[str, str]:
    """Say hello to a user by name."""
    return {"message": f"Hello {name}"}

@app.post("/create_user/", response_model=Dict[str, str])
async def create_user(user_create: UserCreate, db: Session = Depends(db_handler.get_db)) -> Dict[str, str]:
    """Create a new user with the provided name."""
    try:
        user: User = User(name=user_create.name)
        db.add(user)
        db.commit()
        db.refresh(user)

        # Cache the user in Redis
        await redis_handler.set(user_create.name, user_create.name)

        return {"message": f"User {user_create.name} created"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database Error")

@app.get("/user/{name}", response_model=Any)
async def get_user(name: str, db: Session = Depends(db_handler.get_db)) -> Any:
    """Retrieve a user by name, checking Redis cache first."""
    # Check if the user is in Redis cache
    cached_user: Optional[str] = redis_handler.get(name)
    if cached_user:
        return {"message": cached_user}

    # Query the database if not in cache
    try:
        user: Optional[User] = db.query(User).filter(User.name == name).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Cache the user in Redis
        await redis_handler.set(name, name)

        return user
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database Error")
