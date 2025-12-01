import numpy as np
import logging
from typing import Dict, Any, List
import time
import math

from app.config import settings

logger = logging.getLogger(__name__)

class PredictionService:
    """
    Service untuk menjalankan prediksi tsunami menggunakan model SSL-ViT-CNN.
    
    NOTE: Ini adalah implementasi placeholder/demo.
    Untuk production, replace dengan model PyTorch/ONNX yang sudah dilatih.
    """
    
    def __init__(self):
        self.model = None
        self.model_loaded = False
        # self._load_model()  # Uncomment saat model sudah ready
    
    def _load_model(self):
        """
        Load trained model dari file ONNX
        """
        try:
            # TODO: Implement ONNX model loading
            # import onnxruntime as ort
            # self.model = ort.InferenceSession(settings.MODEL_PATH)
            logger.info(f"Loading model from {settings.MODEL_PATH}")
            self.model_loaded = True
            logger.info("✅ Model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            self.model_loaded = False
    
    async def predict(
        self,
        magnitude: float,
        depth: float,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Run tsunami prediction based on earthquake parameters.
        
        Returns:
            Dict containing prediction results with:
            - prediction: {eta, maxWaveHeight, affectedArea, tsunamiCategory, estimatedCasualties}
            - epicenter: {latitude, longitude}
            - inundationZones: List of zones
            - impactZones: List of affected coastal areas
            - waveData: Temporal wave height data
        """
        start_time = time.time()
        logger.info(f"Running prediction for M{magnitude} at ({latitude}, {longitude}), depth={depth}km")
        
        # ========== DEMO IMPLEMENTATION ==========
        # Replace dengan model inference sebenarnya
        
        # Calculate basic tsunami risk
        tsunami_potential = self._assess_tsunami_potential(magnitude, depth)
        
        # Estimate wave parameters
        max_wave_height = self._estimate_wave_height(magnitude, depth)
        eta_minutes = self._estimate_eta(magnitude, depth, latitude, longitude)
        affected_area = self._estimate_affected_area(magnitude, max_wave_height)
        
        # Classify tsunami category
        category = self._classify_tsunami_category(magnitude, max_wave_height)
        
        # Estimate casualties (very rough)
        casualties = self._estimate_casualties(magnitude, max_wave_height, affected_area)
        
        # Generate inundation zones (simplified)
        inundation_zones = self._generate_inundation_zones(latitude, longitude, max_wave_height)
        
        # Get impact zones (coastal cities)
        impact_zones = self._get_impact_zones(latitude, longitude, magnitude, max_wave_height)
        
        # Generate wave temporal data
        wave_data = self._generate_wave_data(eta_minutes, max_wave_height)
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        result = {
            "prediction": {
                "eta": eta_minutes,
                "maxWaveHeight": round(max_wave_height, 2),
                "affectedArea": round(affected_area, 2),
                "tsunamiCategory": category,
                "estimatedCasualties": casualties,
                "processingTimeMs": int(processing_time)
            },
            "epicenter": {
                "latitude": latitude,
                "longitude": longitude
            },
            "inundationZones": inundation_zones,
            "impactZones": impact_zones,
            "waveData": wave_data
        }
        
        logger.info(f"✅ Prediction completed in {processing_time:.0f}ms: Category={category}, ETA={eta_minutes}min")
        return result
    
    def _assess_tsunami_potential(self, magnitude: float, depth: float) -> bool:
        """
        Quick assessment if earthquake can generate tsunami
        """
        # Shallow earthquakes (< 70km) with M > 6.5 have high tsunami potential
        return magnitude >= 6.5 and depth < 70
    
    def _estimate_wave_height(self, magnitude: float, depth: float) -> float:
        """
        Estimate maximum tsunami wave height based on earthquake parameters.
        Simplified formula based on empirical data.
        """
        if magnitude < 6.5:
            return 0.0
        
        # Empirical formula (simplified)
        base_height = (magnitude - 6.0) ** 2.5
        depth_factor = max(0.1, 1.0 - (depth / 100.0))  # Shallower = higher waves
        
        wave_height = base_height * depth_factor * 0.8
        return max(0.0, min(wave_height, 30.0))  # Cap at 30m
    
    def _estimate_eta(self, magnitude: float, depth: float, lat: float, lon: float) -> int:
        """
        Estimate time of arrival to nearest coastline (minutes)
        """
        # Simplified: assume average distance to coast and wave speed
        # Tsunami wave speed: ~sqrt(g * depth) where g=9.8 m/s^2
        # For deep ocean (4000m): ~200 m/s = 720 km/h
        
        # Rough distance to nearest coastline (km)
        # For Selat Sunda epicenter, typical distance is 20-50 km
        distance_km = 30.0  # Placeholder
        
        wave_speed_kmh = 600  # Average tsunami speed
        eta_hours = distance_km / wave_speed_kmh
        eta_minutes = int(eta_hours * 60)
        
        return max(5, min(eta_minutes, 180))  # Between 5-180 minutes
    
    def _estimate_affected_area(self, magnitude: float, wave_height: float) -> float:
        """
        Estimate affected coastal area (km²)
        """
        if wave_height < 0.5:
            return 0.0
        
        # Rough estimate based on magnitude and wave height
        area = (magnitude - 5.0) ** 2 * wave_height * 10
        return max(0.0, min(area, 500.0))  # Cap at 500 km²
    
    def _classify_tsunami_category(self, magnitude: float, wave_height: float) -> str:
        """
        Classify tsunami severity
        """
        if wave_height >= 10.0 or magnitude >= 8.5:
            return "Extreme"
        elif wave_height >= 5.0 or magnitude >= 8.0:
            return "High"
        elif wave_height >= 2.0 or magnitude >= 7.0:
            return "Medium"
        elif wave_height >= 0.5 or magnitude >= 6.5:
            return "Low"
        else:
            return "Minimal"
    
    def _estimate_casualties(self, magnitude: float, wave_height: float, area: float) -> int:
        """
        Very rough estimate of potential casualties
        """
        if wave_height < 1.0:
            return 0
        
        # Assume population density and evacuation rate
        base_casualties = area * wave_height * 20
        return int(min(base_casualties, 10000))  # Cap at 10k
    
    def _generate_inundation_zones(self, lat: float, lon: float, wave_height: float) -> List[Dict]:
        """
        Generate simplified inundation zones
        TODO: Replace with actual GeoJSON polygons from model output
        """
        if wave_height < 0.5:
            return []
        
        # Generate simple circular zones around epicenter
        zones = []
        for i in range(3):
            radius = (i + 1) * 0.05  # degrees
            height = wave_height / (i + 1)
            
            # Simple square polygon (placeholder)
            zones.append({
                "coordinates": [[[
                    [lon - radius, lat - radius],
                    [lon + radius, lat - radius],
                    [lon + radius, lat + radius],
                    [lon - radius, lat + radius],
                    [lon - radius, lat - radius]
                ]]],
                "height": round(height, 2)
            })
        
        return zones
    
    def _get_impact_zones(self, lat: float, lon: float, magnitude: float, wave_height: float) -> List[Dict]:
        """
        Get list of coastal areas that will be impacted
        """
        # Hardcoded coastal cities in Selat Sunda region
        coastal_cities = [
            {"name": "Pantai Anyer", "lat": -6.034, "lon": 105.826},
            {"name": "Labuan", "lat": -6.394, "lon": 105.793},
            {"name": "Carita", "lat": -6.301, "lon": 105.656},
            {"name": "Sumur", "lat": -6.650, "lon": 105.583},
            {"name": "Cilegon", "lat": -6.003, "lon": 106.001},
        ]
        
        impact_zones = []
        for city in coastal_cities:
            # Calculate distance from epicenter
            distance = self._haversine_distance(lat, lon, city["lat"], city["lon"])
            
            if distance < 100:  # Within 100km
                # Estimate wave height at this location (decay with distance)
                local_wave_height = wave_height * math.exp(-distance / 50.0)
                
                if local_wave_height > 0.3:  # Significant wave
                    # Estimate ETA based on distance
                    eta = int(distance / 10) + 5  # Rough estimate
                    
                    impact_zones.append({
                        "name": city["name"],
                        "distance": round(distance, 1),
                        "eta": eta,
                        "waveHeight": round(local_wave_height, 2)
                    })
        
        return sorted(impact_zones, key=lambda x: x["eta"])
    
    def _generate_wave_data(self, eta_minutes: int, max_wave_height: float) -> List[Dict]:
        """
        Generate temporal wave height data for visualization
        """
        time_points = range(0, min(eta_minutes + 30, 120), 5)  # Every 5 minutes
        wave_data = []
        
        for t in time_points:
            # Simplified wave propagation (sinusoidal + growth)
            if t < eta_minutes:
                # Before arrival: small background waves
                height = 0.2 + 0.1 * np.sin(t / 10.0)
            else:
                # After arrival: main tsunami wave
                time_since_arrival = t - eta_minutes
                # Peak at arrival, then decay
                decay = np.exp(-time_since_arrival / 20.0)
                oscillation = np.sin(time_since_arrival / 5.0)
                height = max_wave_height * decay * (0.7 + 0.3 * oscillation)
            
            wave_data.append({
                "time": t,
                "waveHeight": round(max(0.0, height), 2)
            })
        
        return wave_data
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points on Earth (km)
        """
        R = 6371  # Earth radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
