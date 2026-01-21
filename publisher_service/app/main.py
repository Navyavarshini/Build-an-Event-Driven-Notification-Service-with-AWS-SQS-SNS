from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.v1 import events

app = FastAPI()

app.include_router(events.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ REQUIRED: Convert FastAPI 422 → 400 with custom error format
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []

    for error in exc.errors():
        field = error.get("loc", [])[-1]
        message = error.get("msg", "Invalid value")
        details.append(f"'{field}' {message}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Invalid request payload",
            "details": details
        },
    )
