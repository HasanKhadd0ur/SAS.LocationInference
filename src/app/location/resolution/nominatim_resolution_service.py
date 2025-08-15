from time import sleep
import requests
from app.core.configs.base_config import BaseConfig
from app.location.factory.services_factory import get_location_recognizer_service
from app.core.models.location import Location
from app.location.base.resolution_service_base import IResolutionService


class NominatimResolutionService(IResolutionService):
    def __init__(self, config: BaseConfig):
        self.config = config

    def clean_location(self, loc: str) -> str:
        return loc.strip()
    
    
    def geocode(self, location: str) -> Location:
            locs_raw = location.split(",")
            seen = set()
            unique_locs = []
            for loc in locs_raw:
                loc_clean = self.clean_location(loc)
                loc_lower = loc_clean.lower()
                if loc_lower not in seen and len(loc_clean) > 2:
                    unique_locs.append(loc_clean)
                    seen.add(loc_lower)

            latitudes = []
            longitudes = []

            url = self.config.get_geocoding_service_url()
            headers = {
                "User-Agent": self.config.get_random_user_agent()
            }

            for loc in unique_locs:
                params = {
                    "q": loc,
                    "format": "json",
                    "limit": 1
                }
                try:
                    sleep(1)  # rate limit / delay
                    response = requests.get(url, params=params, headers=headers)
                    response.raise_for_status()
                    results = response.json()

                    if results:
                        result = results[0]
                        latitudes.append(float(result["lat"]))
                        longitudes.append(float(result["lon"]))
                except requests.RequestException:
                    continue

            if not latitudes or not longitudes:
                
                # Return a syria location if no valid ones found
                random_lat = 34.34
                random_lon = 43.34
                return Location(latitude=random_lat, longitude=random_lon)

            avg_lat = sum(latitudes) / len(latitudes)
            avg_lon = sum(longitudes) / len(longitudes)

            return Location(latitude=avg_lat, longitude=avg_lon)
