from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1 import health, simulation, realtime, history

# ============================================
# FastAPI App Instance
# ============================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    description="WebGIS Simulasi Prediksi Tsunami Selat Sunda dengan SSL-ViT-CNN",
)

# ============================================
# CORS Middleware
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Root Endpoint
# ============================================
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AVATAR Tsunami Prediction API is running",
        "version": settings.VERSION,
        "status": "healthy",
    }

# ============================================
# Include All Routers
# ============================================
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["Simulation"])
app.include_router(realtime.router, prefix="/api/v1/earthquakes", tags=["Real-Time"])
app.include_router(history.router, prefix="/api/v1/history", tags=["History"])
