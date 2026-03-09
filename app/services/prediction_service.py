import numpy as np
import logging
from typing import Dict, Any, List, Optional
import time
import os
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
        self._load_model()
    
    def _load_model(self):
        """
        Load trained model dari file ONNX
        """
        try:
            import onnxruntime as ort
            model_path = settings.MODEL_PATH
            # Ensure path is absolute or relative to cwd
            if not os.path.exists(model_path):
                 # Try relative to project root
                 model_path = os.path.join(settings.BASE_DIR, settings.MODEL_PATH)
            
            if os.path.exists(model_path):
                self.model = ort.InferenceSession(model_path)
                self.model_loaded = True
                logger.info(f"✅ Model loaded successfully from {model_path}")
            else:
                logger.error(f"❌ Model file not found at {model_path}")
                self.model_loaded = False
                
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            self.model_loaded = False
    
    async def predict(
        self,
        magnitude: float,
        depth: float,
        latitude: float,
        longitude: float,
        mode: str = "AI"
    ) -> Dict[str, Any]:
        """
        Run tsunami prediction using ONNX model (AI) or Heuristics (General).
        """
        start_time = time.time()
        logger.info(f"Running prediction [{mode}] for M{magnitude} at ({latitude}, {longitude}), depth={depth}km")
        
        model_max_wave = 0.0
        ai_wave_grid = None  # Akan diisi 128x128 grid dari AI jika berhasil
        
        # ============================================
        # MODE 1: AI (Selat Sunda Only)
        # ============================================
        if mode == "AI" and self.model_loaded:
            try:
                # 1. Prepare Input for Model
                # Map lat/lon to grid coordinates (0-127)
                bounds = settings.SUNDA_STRAIT_BOUNDS
                lat_range = bounds["max_lat"] - bounds["min_lat"]
                lon_range = bounds["max_lon"] - bounds["min_lon"]
                
                # Normalize coordinates 0-1
                norm_x = (longitude - bounds["min_lon"]) / lon_range
                norm_y = (latitude - bounds["min_lat"]) / lat_range
                
                # Grid size
                H, W = 128, 128
                grid_x = int(norm_x * W)
                grid_y = int(norm_y * H)
                
                # Clamp to grid
                grid_x = max(0, min(grid_x, W-1))
                grid_y = max(0, min(grid_y, H-1))
                
                # Create input tensor
                input_tensor = np.zeros((1, 128, 128, 2), dtype=np.float32)
                
                # Create Gaussian bump
                x = np.linspace(0, W-1, W)
                y = np.linspace(0, H-1, H)
                xv, yv = np.meshgrid(x, y)
                
                # Sigma depends on magnitude
                sigma = (magnitude - 5.0) * 2.0
                if sigma < 1.0: sigma = 1.0
                
                gaussian = np.exp(-((xv - grid_x)**2 + (yv - grid_y)**2) / (2 * sigma**2))
                displacement = gaussian * (magnitude - 5.0) 
                
                input_tensor[0, :, :, 0] = displacement
                input_tensor[0, :, :, 1] = 0.5  # Constant normalized depth
                
                # 2. Run Inference
                input_name = self.model.get_inputs()[0].name
                outputs = self.model.run(None, {input_name: input_tensor})
                
                wave_grid = outputs[0][0, :, :, 0] # Extract 128x128 grid
                ai_wave_grid = wave_grid            # ✅ Capture untuk inundation contours
                model_max_wave = np.max(wave_grid)
                
                # Calibrate/Normalize
                model_max_wave = float(model_max_wave)
                logger.info(f"AI Model Result: {model_max_wave}m (wave_grid captured)")

            except Exception as e:
                logger.error(f"AI Inference failed: {e}")
                # Fallback
                model_max_wave = self._estimate_wave_height(magnitude, depth)

        # ============================================
        # MODE 2: HEURISTIC (General Locations)
        # ============================================
        else:
            logger.info("Using Heuristic Mode (General)")
            model_max_wave = self._estimate_wave_height(magnitude, depth)

        # 3. Finalize Output
        # Use model output or fallback estimate if model output is suspicious (too low/high)
        # For simplicity, we trust the chosen method
        max_wave_height = model_max_wave
        
        # Recalculate derived metrics
        eta_minutes = self._estimate_eta(magnitude, depth, latitude, longitude)
        affected_area = self._estimate_affected_area(magnitude, max_wave_height)
        category = self._classify_tsunami_category(magnitude, max_wave_height)
        casualties = self._estimate_casualties(magnitude, max_wave_height, affected_area)
        
        # Generate contour zones dari AI wave_grid (atau fallback ke ellipse halus)
        inundation_zones = self._generate_inundation_zones(latitude, longitude, max_wave_height, wave_grid=ai_wave_grid)
        impact_zones = self._get_impact_zones(latitude, longitude, magnitude, max_wave_height)
        wave_data = self._generate_wave_data(eta_minutes, max_wave_height)
        
        processing_time = (time.time() - start_time) * 1000
        
        result = {
            "prediction": {
                "eta": eta_minutes,
                "maxWaveHeight": round(max_wave_height, 2),
                "affectedArea": round(affected_area, 2),
                "tsunamiCategory": category,
                "estimatedCasualties": casualties,
                "processingTimeMs": int(processing_time),
                "modelUsed": "ONNX: Tsunami-ViT" if self.model_loaded else "Heuristic Fallback"
            },
            "epicenter": {
                "latitude": latitude,
                "longitude": longitude
            },
            "inundationZones": inundation_zones,
            "impactZones": impact_zones,
            "waveData": wave_data
        }
        
        logger.info(f"✅ Prediction completed: Category={category}, MaxWave={max_wave_height:.2f}m")
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
    
    def _generate_inundation_zones(
        self,
        lat: float,
        lon: float,
        wave_height: float,
        wave_grid: Optional[np.ndarray] = None
    ) -> List[Dict]:
        """
        Generate inundation zone polygons.
        - Mode AI  : Ekstrak kontur dari wave_grid 128x128 via Marching Squares (scikit-image).
        - Mode Fallback: 3 ellipsis konsentris halus (jauh lebih baik dari kotak).
        """
        if wave_height < 0.5:
            return []

        # ── Mode 1: AI Contour (Marching Squares dari wave_grid) ──────────────
        if wave_grid is not None:
            try:
                from skimage import measure
                from app.config import settings

                bounds = settings.SUNDA_STRAIT_BOUNDS
                min_lat = bounds["min_lat"]
                max_lat = bounds["max_lat"]
                min_lon = bounds["min_lon"]
                max_lon = bounds["max_lon"]
                H, W = wave_grid.shape  # 128 x 128

                grid_max = float(np.max(wave_grid))
                if grid_max < 1e-6:
                    raise ValueError("wave_grid kosong/flat, gunakan fallback")

                # 3 level kontur: 30%, 55%, 80% dari nilai puncak
                thresholds = [
                    (grid_max * 0.30, wave_height * 1.0),   # zona luar  (rendah)
                    (grid_max * 0.55, wave_height * 0.6),   # zona tengah (sedang)
                    (grid_max * 0.80, wave_height * 0.3),   # zona dalam  (tinggi)
                ]

                zones = []
                for level, height_at_level in thresholds:
                    contours = measure.find_contours(wave_grid, level=level)
                    if not contours:
                        continue

                    # Ambil kontur terbesar di level ini
                    largest = max(contours, key=lambda c: len(c))
                    if len(largest) < 4:
                        continue

                    # Konversi piksel grid (row, col) → koordinat lat/lon nyata
                    ring = []
                    for row, col in largest:
                        real_lon = min_lon + (col / (W - 1)) * (max_lon - min_lon)
                        real_lat = min_lat + (row / (H - 1)) * (max_lat - min_lat)
                        ring.append([round(real_lon, 6), round(real_lat, 6)])

                    # Tutup ring (GeoJSON: titik pertama == titik terakhir)
                    ring.append(ring[0])

                    zones.append({
                        "coordinates": [ring],
                        "height": round(height_at_level, 2)
                    })

                if zones:
                    logger.info(f"✅ Kontur inundasi: {len(zones)} zona dari wave_grid AI")
                    return zones

            except Exception as e:
                logger.warning(f"⚠️ Ekstraksi kontur gagal, fallback ke ellipse: {e}")

        # ── Mode 2: Fallback – Ellipsis halus (bukan kotak) ────────────────────
        logger.info("Menggunakan ellipsis fallback untuk inundation zones")
        zones = []
        # semi_lon, semi_lat = setengah sumbu ellipsis dalam derajat
        ellipse_params = [
            (0.20, 0.13, wave_height * 1.0),   # luar
            (0.13, 0.08, wave_height * 0.6),   # tengah
            (0.07, 0.045, wave_height * 0.3),  # dalam
        ]
        n_points = 36  # 36 titik = lingkaran halus
        for semi_lon, semi_lat, height_at_level in ellipse_params:
            ring = []
            for i in range(n_points):
                angle = 2 * math.pi * i / n_points
                ring.append([
                    round(lon + semi_lon * math.cos(angle), 6),
                    round(lat + semi_lat * math.sin(angle), 6)
                ])
            ring.append(ring[0])  # tutup ring
            zones.append({
                "coordinates": [ring],
                "height": round(height_at_level, 2)
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
