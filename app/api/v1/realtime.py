from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
import logging

from app.services.earthquake_service import EarthquakeService
from app.database.connection import get_db
from app.database import crud

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/realtime")
async def get_realtime_earthquakes(
    limit: int = Query(default=50, ge=1, le=100),
    min_magnitude: Optional[float] = Query(default=2.0, ge=1.0),
    hours: int = Query(default=24, ge=1, le=168),  # Max 1 week
    db: AsyncSession = Depends(get_db)
):
    """
    Mendapatkan data gempa real-time dari BMKG/USGS.
    
    Parameters:
    - limit: Jumlah maksimum data gempa (default: 10)
    - min_magnitude: Magnitudo minimum (default: 5.0)
    - hours: Rentang waktu dalam jam (default: 24)
    """
    logger.info(f"Serving realtime earthquakes from DB: limit={limit}")
    
    try:
        # Get from database (populated by scheduler)
        earthquakes = await crud.get_earthquake_history(db, limit=limit)
        
        # Analyze tsunami risk for each earthquake
        analyzed_earthquakes = []
        for eq in earthquakes:
            # Simple risk assessment
            risk_level = "Rendah"
            max_wave_height = 0.0
            
            # Convert timestamp to aware datetime if naive (for calculation)
            # SQLAlchemy returns naive for timestamp without timezone
            
            if eq['magnitude'] >= 7.5 and eq['depth'] < 50:
                risk_level = "Bahaya"
                max_wave_height = (eq['magnitude'] - 6.5) * 2
            elif eq['magnitude'] >= 7.0 and eq['depth'] < 70:
                risk_level = "Sedang"
                max_wave_height = (eq['magnitude'] - 6.0) * 1.5
            
            # Add risk info
            eq["riskLevel"] = risk_level
            eq["maxWaveHeight"] = round(max_wave_height, 2)
            analyzed_earthquakes.append(eq)
        
        return {
            "status": "success",
            "earthquakes": analyzed_earthquakes,
            "count": len(analyzed_earthquakes),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error serving realtime data: {e}", exc_info=True)
        return {
            "status": "error",
            "earthquakes": [],
            "message": str(e)
        }

@router.get("/earthquakes/{earthquake_id}")
async def get_earthquake_detail(
    earthquake_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Mendapatkan detail gempa berdasarkan ID
    """
    earthquake = await crud.get_earthquake_by_id(db, earthquake_id)
    
    if not earthquake:
        return {
            "status": "error",
            "message": "Data gempa tidak ditemukan"
        }
    
    return {
        "status": "success",
        "data": earthquake
    }
