from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from auth.views import router as auth_router
from animals.views import router as animals_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(animals_router)


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5555, reload=True)
