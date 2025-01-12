from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.routes.auth import router as auth_router
from src.routes.contacts import router as contacts_router
from src.settings import settings


ROUTERS = [auth_router, contacts_router]

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.errors(),
        },
    )


for router in ROUTERS:
    app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
