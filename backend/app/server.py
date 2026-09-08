from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Queue System")

# Minimal CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import registration, auth, staff, status, display, occupancy

app.include_router(registration.router, prefix="/api")
app.include_router(auth.router, prefix="/api/auth")
app.include_router(staff.router, prefix="/api/staff")
app.include_router(status.router, prefix="/api/status")
app.include_router(display.router, prefix="/api/display")
app.include_router(occupancy.router, prefix="/api")

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
