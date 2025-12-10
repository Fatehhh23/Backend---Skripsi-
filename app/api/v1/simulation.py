from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.services.prediction_service import PredictionService
from app.database.connection import get_db
from app.database import crud
from app.utils.validators import validate_earthquake_params

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/simulation/run", response_model=SimulationResponse)
async def run_simulation(
    request_data: SimulationRequest,
    background_tasks: BackgroundTasks,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint untuk menjalankan simulasi tsunami manual.
    
    Parameters:
    - magnitude: Magnitudo gempa (3.0 - 9.5)
    - depth: Kedalaman gempa dalam km (1 - 700)
    - latitude: Koordinat lintang (-90 to 90)
    - longitude: Koordinat bujur (-180 to 180)
    
    Returns:
    - Hasil prediksi tsunami termasuk ETA, tinggi gelombang, zona genangan
    """
    logger.info(f"Simulation request: M{request_data.magnitude} at ({request_data.latitude}, {request_data.longitude})")
    
    # Validate input parameters
    try:
        validate_earthquake_params(
            request_data.magnitude,
            request_data.depth,
            request_data.latitude,
            request_data.longitude
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        # Initialize prediction service
        prediction_service = PredictionService()
        
        # Run prediction
        result = await prediction_service.predict(
            magnitude=request_data.magnitude,
            depth=request_data.depth,
            latitude=request_data.latitude,
            longitude=request_data.longitude
        )
        
        # Get client IP address
        client_ip = req.client.host if req.client else None
        
        # Get processing time from result
        processing_time_ms = result.get('prediction', {}).get('processingTimeMs', None)
        
        # Save to database (background task)
        background_tasks.add_task(
            crud.save_simulation_result,
            db=db,
            params=request_data.dict(),
            result=result,
            processing_time_ms=processing_time_ms,
            user_session_id=None,  # TODO: Implement session tracking
            ip_address=client_ip
        )
        
        logger.info(f"Simulation completed: ETA={result['prediction']['eta']}min")
        
        return SimulationResponse(
            status="success",
            data=result,
            message="Simulasi berhasil dijalankan"
        )
        
    except Exception as e:
        logger.error(f"Simulation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menjalankan simulasi: {str(e)}"
        )

@router.get("/simulation/{simulation_id}")
async def get_simulation(
    simulation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Mendapatkan detail simulasi berdasarkan ID
    """
    simulation = await crud.get_simulation_by_id(db, simulation_id)
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulasi tidak ditemukan")
    
    return {
        "status": "success",
        "data": simulation
    }
