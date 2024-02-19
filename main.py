"""
In the main.py file, the FastAPI application is initialized, including the routes, middleware, and dependencies.
The uvicorn library is used to run the application.
"""

import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter

from src.conf.config import settings
from src.routes import contacts, auth, users

app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix='/api')

app.mount("/src/static", StaticFiles(directory="src/static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup() -> None:
    """
    Initializes the redis connection for fastapi-limiter.
    :return: None
    """
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0,
                          encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(r)


@app.get("/")
def read_root() -> dict:
    """
    Returns the root of the API. It is the entry point for the application.
    :return: dict
    """
    return {"message": "This is API for contacts"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
