from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from pydantic import ValidationError
from starlette.responses import JSONResponse

from animals.views.species import router as species_router
from animals.views.animals import router as animals_router
from auth.views import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = []
    for error in exc.errors():
        field_path = ".".join(map(str, error['loc']))
        errors.append({"field": field_path, "message": error['msg']})

    return JSONResponse(
        status_code=422,
        content={"error_type": "ValidationError", "errors": errors}
    )


app.include_router(auth_router)
app.include_router(animals_router)
app.include_router(species_router)


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5555, reload=True)
