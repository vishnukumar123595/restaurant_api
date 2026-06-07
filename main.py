"""
Restaurant Orders API
=====================
Run:   uvicorn main:app --reload
Docs:  http://127.0.0.1:8000/docs
"""

import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import engine
from app.models.models import Base
from app.routers import orders

Base.metadata.create_all(bind=engine)

# ── Tag descriptions (shown in Swagger UI) ────────────────────────────────────
tags_metadata = [
    {
        "name": "Orders",
        "description": (
            "Core endpoints. Returns full order details — line items (item name, "
            "category, size, unit price, qty) **and** all payment records (type, "
            "status, tips, discounts) in a single response.\n\n"
            "**Performance:** Uses `joinedload()` to fetch all related data in one "
            "SQL round-trip, avoiding N+1 queries. Results are paginated.\n\n"
            "**Auth:** All routes require `X-API-Key` header. "
            "Click the **Authorize** button and enter the key."
        ),
    },
    {
        "name": "System",
        "description": "Health check — no authentication required.",
    },
]

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Restaurant Orders API",
    description="""
A FastAPI service exposing order history, item details, and payment records
from a restaurant POS system.

---

## Authentication

Every protected endpoint requires an **API Key** in the request header:

```
X-API-Key: restaurant-secret-key-2025
```

**Steps to authenticate in Swagger:**
1. Click the green **Authorize** button (top right)
2. Enter `restaurant-secret-key-2025`
3. Click **Authorize**, then **Close**
4. All locked endpoints will now include the key automatically

---

## Data Summary

| Entity | Records |
|--------|---------|
| Orders | 11 |
| Order line items | 52 |
| Payments | 17 |
| Menu items | 10 |
| Categories | 5 |

---

## Performance Features

- Pagination on all list endpoints (no unbounded queries)
- `joinedload()` prevents N+1 queries — all data fetched in one round-trip
- Explicit indexes on `order_status`, `payment_status`, `order_date`, `order_id` FKs
- GZip compression on responses over 500 bytes
- `X-Process-Time` header on every response shows server latency
- `X-Request-ID` header on every response for request traceability
    """,
    version="1.0.0",
    contact={"name": "Vishnu", "email": "dev@restaurant.com"},
    openapi_tags=tags_metadata,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten to specific origins in production
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=500)


@app.middleware("http")
async def add_observability_headers(request: Request, call_next):
    """
    Adds two headers to every response:
      X-Request-ID   — unique ID per request (use for log correlation / debugging)
      X-Process-Time — server processing time in seconds (visible in Postman)
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()

    response = await call_next(request)

    response.headers["X-Request-ID"]   = request_id
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}s"
    return response


# ── Global Exception Handlers ─────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """
    Returns a clean 422 when query params or path params fail validation
    (e.g. page=-1, non-integer order_id).
    """
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "One or more request parameters are invalid.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(request: Request, exc: SQLAlchemyError):
    """
    Catches any unexpected database errors and returns a safe 500
    without exposing internal SQL details to the client.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Database Error",
            "message": "An unexpected database error occurred. Please try again.",
            "request_id": request.headers.get("X-Request-ID", "N/A"),
        },
    )


@app.exception_handler(Exception)
async def global_error_handler(request: Request, exc: Exception):
    """
    Catch-all for any unhandled exception.
    Returns 500 with a safe message — never exposes stack traces.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred.",
            "request_id": request.headers.get("X-Request-ID", "N/A"),
        },
    )


# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(orders.router)


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    description="Returns `200 OK` if the server is running. No authentication required.",
)
def health():
    return {
        "status": "ok",
        "service": "Restaurant Orders API",
        "version": "1.0.0",
    }
