from fastapi import FastAPI
import uvicorn

from src.config import settings
from src.users.router import router as users_router
from src.url_shortener.routers import url_router

app = FastAPI()
app.include_router(users_router)
app.include_router(url_router)

if __name__ == "__main__":
    uvicorn.run(
        app="src.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT
    )
