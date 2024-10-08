from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User
import redis
from typing import Dict, Any

app = FastAPI(root_path="/api")  # Same as nginx location

# Redis configuration
redis_host: str = "redis"
redis_port: int = 6379
redis_client: redis.StrictRedis = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

# Database configuration
DATABASE_URL: str = "sqlite:///./db/test.db"
engine = create_engine(DATABASE_URL)

SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables
Base.metadata.create_all(bind=engine)


@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint returning a simple message."""
    return {"message": "Hello World"}


@app.get("/hello/{name}", response_model=Dict[str, str])
async def say_hello(name: str) -> Dict[str, str]:
    """Say hello to a user by name."""
    return {"message": f"Hello {name}"}


@app.post("/create_user/{name}", response_model=Dict[str, str])
async def create_user(name: str) -> Dict[str, str]:
    """Create a new user with the provided name."""
    try:
        with SessionLocal() as session:  # type: Session
            user: User = User(name=name)
            session.add(user)
            session.commit()

        # Cache the user in Redis
        await redis_client.set(name, name)

        return {"message": f"User {name} created"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database Error")


@app.get("/user/{name}", response_model=Any)
async def get_user(name: str) -> Any:
    """Retrieve a user by name, checking Redis cache first."""
    # Check if the user is in Redis cache
    cached_user: bytes | None = redis_client.get(name)
    if cached_user:
        return {"message": cached_user.decode('utf-8')}

    # Query the database if not in cache
    try:
        with SessionLocal() as session:  # type: Session
            user: User | None = session.query(User).filter(User.name == name).first()
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")

        # Cache the user in Redis
        await redis_client.set(name, name)

        return user
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database Error")
