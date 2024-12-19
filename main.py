from fastapi import FastAPI

from src.routes.contacts import router as contacts_router


ROUTERS = [contacts_router]

app = FastAPI()

for router in ROUTERS:
    app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
