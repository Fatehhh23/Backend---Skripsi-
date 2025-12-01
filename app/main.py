from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from app.config import settings
from app.api.v1 import simulation, realtime, history, health
from app.database.connection import init_db, close_db
from app.services.background_tasks import start_background_monitor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AVATAR Backend API...")
    await init_db()
    
    # Start background monitoring service (optional)
    if settings.ENABLE_REALTIME_MONITORING:
        await start_background_monitor()
    
    logger.info("✅ Backend API ready")
    yield
    
    # Shutdown
    logger.info("Shutting down AVATAR Backend API...")
    await close_db()
    logger.info("✅ Shutdown complete")

app = FastAPI(
    title="AVATAR - Tsunami Prediction API",
    description="WebGIS Simulasi Prediksi Tsunami Selat Sunda dengan SSL-ViT-CNN",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(simulation.router, prefix="/api/v1", tags=["Simulation"])
app.include_router(realtime.router, prefix="/api/v1", tags=["Real-Time"])
app.include_router(history.router, prefix="/api/v1", tags=["History"])

@app.get("/")
async def root():
    return {
        "message": "AVATAR Tsunami Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
