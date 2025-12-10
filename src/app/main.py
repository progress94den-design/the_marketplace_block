import uvicorn
from fastapi import FastAPI, Request

from src.app.api.router import api_router
from src.app.core.middleware import AuthMiddleware

main_api_router = FastAPI(title="The Marketplace Blog")
# main_api_router.middleware("http")(AuthMiddleware)
main_api_router.middleware(AuthMiddleware)

main_api_router.include_router(api_router, prefix="/api/v1", tags=["/api/v1"])

@main_api_router.get("/ping")
def ping():
    return {"status": "ok"}


if __name__ == "__main__":
    # run app on the host and port
    uvicorn.run(main_api_router, host="localhost", port=8000)
    # uvicorn.run("main:app", host="0.0.0.0", port=8010)
