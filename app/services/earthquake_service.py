import aiohttp
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import hashlib

from app.config import settings

logger = logging.getLogger(__name__)

class EarthquakeService:
    """
    Service untuk fetch data gempa dari BMKG atau USGS
    """
    
    def __init__(self):
        self.bmkg_url = settings.BMKG_API_URL
        self.usgs_url = settings.USGS_API_URL
        self.timeout = aiohttp.ClientTimeout(total=settings.API_TIMEOUT)
    
    async def fetch_recent_earthquakes(
        self,
        min_magnitude: float = 5.0,
        hours: int = 24,
        limit: int = 10,
        source: str = "usgs"  # "bmkg" or "usgs"
    ) -> List[Dict[str, Any]]:
        """
        Fetch recent earthquakes from external API
        """
        logger.info(f"Fetching earthquakes from {source.upper()}: M>={min_magnitude}, last {hours}h")
        
        try:
            if source.lower() == "bmkg":
                earthquakes = await self._fetch_from_bmkg()
            else:
                earthquakes = await self._fetch_from_usgs(min_magnitude, hours)
            
            # Filter and sort
            filtered = [
                eq for eq in earthquakes
                if eq['magnitude'] >= min_magnitude
            ]
            filtered.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return filtered[:limit]
            
        except Exception as e:
            logger.error(f"Error fetching earthquakes from {source}: {e}", exc_info=True)
            # Return demo data as fallback
            return self._get_demo_data(limit)
    
    async def _fetch_from_bmkg(self) -> List[Dict[str, Any]]:
        """
        Fetch dari BMKG (format XML/RSS)
        """
        url = f"{self.bmkg_url}autogempa.xml"
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"BMKG API returned status {response.status}")
                
                content = await response.text()
                return self._parse_bmkg_xml(content)
    
    def _parse_bmkg_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """
        Parse XML response dari BMKG
        """
        try:
            root = ET.fromstring(xml_content)
            earthquakes = []
            
            for item in root.findall('.//item'):
                # Extract data from XML
                title = item.find('title').text if item.find('title') is not None else ""
                description = item.find('description').text if item.find('description') is not None else ""
                pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ""
                
                # Parse magnitude, coordinates, depth from description
                # Format biasanya: "Magnitude: 5.2, Kedalaman: 10 km, Lokasi: ..."
                # TODO: Implement proper parsing
                
                earthquakes.append({
                    'id': hashlib.md5(title.encode()).hexdigest()[:16],
                    'magnitude': 5.0,  # Placeholder
                    'depth': 10.0,
                    'latitude': -6.5,
                    'longitude': 105.3,
                    'timestamp': datetime.utcnow(),
                    'location': title,
                    'source': 'BMKG'
                })
            
            return earthquakes
            
        except Exception as e:
            logger.error(f"Error parsing BMKG XML: {e}")
            return []
    
    async def _fetch_from_usgs(self, min_magnitude: float, hours: int) -> List[Dict[str, Any]]:
        """
        Fetch dari USGS Earthquake API
        """
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # USGS query parameters
        params = {
            'format': 'geojson',
            'starttime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'endtime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'minmagnitude': min_magnitude,
            'minlatitude': settings.SUNDA_STRAIT_BOUNDS['min_lat'],
            'maxlatitude': settings.SUNDA_STRAIT_BOUNDS['max_lat'],
            'minlongitude': settings.SUNDA_STRAIT_BOUNDS['min_lon'],
            'maxlongitude': settings.SUNDA_STRAIT_BOUNDS['max_lon'],
            'orderby': 'time-asc'
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            async with session.get(self.usgs_url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"USGS API returned status {response.status}")
                
                data = await response.json()
                return self._parse_usgs_geojson(data)
    
    def _parse_usgs_geojson(self, geojson: Dict) -> List[Dict[str, Any]]:
        """
        Parse GeoJSON response dari USGS
        """
        earthquakes = []
        
        for feature in geojson.get('features', []):
            props = feature.get('properties', {})
            coords = feature.get('geometry', {}).get('coordinates', [])
            
            if len(coords) >= 3:
                earthquakes.append({
                    'id': feature.get('id', ''),
                    'magnitude': props.get('mag', 0.0),
                    'depth': abs(coords[2]),  # depth is negative in USGS
                    'latitude': coords[1],
                    'longitude': coords[0],
                    'timestamp': datetime.fromtimestamp(props.get('time', 0) / 1000),
                    'location': props.get('place', 'Unknown'),
                    'source': 'USGS'
                })
        
        return earthquakes
    
    def _get_demo_data(self, limit: int) -> List[Dict[str, Any]]:
        """
        Return demo earthquake data for testing
        """
        import random
        
        demo_earthquakes = []
        base_time = datetime.utcnow()
        
        locations = [
            "52 km Barat Daya Sumur-Banten",
            "45 km Selatan Pandeglang-Banten",
            "38 km Barat Laut Labuan-Banten",
            "62 km Tenggara Anyer-Banten",
            "41 km Timur Laut Cilegon-Banten"
        ]
        
        for i in range(min(limit, 5)):
            demo_earthquakes.append({
                'id': f'demo-{i+1}',
                'magnitude': round(random.uniform(5.0, 7.5), 1),
                'depth': round(random.uniform(10.0, 50.0), 1),
                'latitude': round(random.uniform(-6.8, -6.0), 3),
                'longitude': round(random.uniform(105.0, 106.0), 3),
                'timestamp': base_time - timedelta(hours=i * 2),
                'location': random.choice(locations),
                'source': 'DEMO'
            })
        
        return demo_earthquakes
