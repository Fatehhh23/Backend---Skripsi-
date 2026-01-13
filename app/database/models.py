from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
# from geoalchemy2 import Geometry  # TEMP: Commented out - requires GDAL/PROJ libraries
from datetime import datetime
import uuid

from app.database.connection import Base

class Simulation(Base):
    """Model untuk menyimpan riwayat simulasi"""
    __tablename__ = "simulations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Input parameters
    magnitude = Column(Float, nullable=False)
    depth = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Epicenter as PostGIS Point
    # TEMP: Commented out - requires geoalchemy2
    # epicenter = Column(Geometry('POINT', srid=4326), nullable=True)
    
    # Prediction results (stored as JSON)
    prediction_data = Column(JSON, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_session_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    # Processing metrics
    processing_time_ms = Column(Integer, nullable=True)
    model_version = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<Simulation {self.id}: M{self.magnitude} at ({self.latitude}, {self.longitude})>"

class Earthquake(Base):
    """Model untuk menyimpan data gempa real-time"""
    __tablename__ = "earthquakes"
    
    id = Column(String(100), primary_key=True)  # ID from BMKG/USGS
    
    # Earthquake parameters
    magnitude = Column(Float, nullable=False)
    depth = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Location as PostGIS Point
    # TEMP: Commented out - requires geoalchemy2
    # location = Column(Geometry('POINT', srid=4326), nullable=True)
    
    # Metadata
    location_name = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    source = Column(String(50), nullable=False)  # BMKG or USGS
    
    # Tsunami assessment (if analyzed)
    tsunami_potential = Column(Boolean, default=False)
    tsunami_risk_level = Column(String(50), nullable=True)  # Rendah, Sedang, Bahaya
    max_wave_height = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Earthquake {self.id}: M{self.magnitude} at {self.timestamp}>"

class InundationZone(Base):
    """Model untuk menyimpan zona genangan tsunami"""
    __tablename__ = "inundation_zones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key to Simulation
    
    # Geometry as PostGIS Polygon
    # TEMP: Commented out - requires geoalchemy2
    # geometry = Column(Geometry('POLYGON', srid=4326), nullable=False)
    
    # Wave characteristics
    wave_height = Column(Float, nullable=False)  # meter
    arrival_time = Column(Integer, nullable=False)  # minutes
    
    # Area statistics
    area_sqkm = Column(Float, nullable=True)
    affected_population = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<InundationZone {self.id}: {self.wave_height}m>"

class CoastlineData(Base):
    """Model untuk data garis pantai (reference data)"""
    __tablename__ = "coastlines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    
    # Coastline as PostGIS LineString
    # TEMP: Commented out - requires geoalchemy2
    # geometry = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    
    # Metadata
    region = Column(String(100), nullable=True)
    length_km = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Coastline {self.name}>"
