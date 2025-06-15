"""eBird API integration for species data."""

import logging
import os
from typing import Dict, List, Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)


class eBirdAPI:
    """Handle eBird API requests for species data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize eBird API handler.
        
        Args:
            api_key: eBird API key (can also be set via EBIRD_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('EBIRD_API_KEY')
        self.base_url = "https://api.ebird.org/v2"
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'X-eBirdApiToken': self.api_key
            })
        else:
            logger.warning("No eBird API key provided - some features will be limited")
    
    def get_recent_observations_by_hotspot(
        self, 
        hotspot_id: str, 
        days_back: int = 30,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Get recent observations from a specific hotspot.
        
        Args:
            hotspot_id: eBird hotspot identifier (e.g., 'L12345')
            days_back: Number of days back to search
            max_results: Maximum number of results
            
        Returns:
            List of observation records
        """
        if not self.api_key:
            raise ValueError("eBird API key required for hotspot observations")
        
        url = f"{self.base_url}/data/obs/{hotspot_id}/recent"
        params = {
            'back': days_back,
            'maxResults': max_results
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            observations = response.json()
            logger.info(f"Retrieved {len(observations)} observations from hotspot {hotspot_id}")
            
            return observations
            
        except requests.RequestException as e:
            logger.error(f"Error fetching hotspot observations: {e}")
            return []
    
    def get_recent_observations_by_region(
        self,
        region_code: str,
        days_back: int = 30,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Get recent observations from a region.
        
        Args:
            region_code: eBird region code (e.g., 'US-NY')
            days_back: Number of days back to search
            max_results: Maximum number of results
            
        Returns:
            List of observation records
        """
        if not self.api_key:
            raise ValueError("eBird API key required for regional observations")
        
        url = f"{self.base_url}/data/obs/{region_code}/recent"
        params = {
            'back': days_back,
            'maxResults': max_results
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            observations = response.json()
            logger.info(f"Retrieved {len(observations)} observations from region {region_code}")
            
            return observations
            
        except requests.RequestException as e:
            logger.error(f"Error fetching regional observations: {e}")
            return []
    
    def get_hotspot_info(self, hotspot_id: str) -> Optional[Dict]:
        """
        Get information about a specific hotspot.
        
        Args:
            hotspot_id: eBird hotspot identifier
            
        Returns:
            Hotspot information dictionary or None if not found
        """
        if not self.api_key:
            logger.warning("eBird API key recommended for hotspot info")
        
        url = f"{self.base_url}/ref/hotspot/info/{hotspot_id}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching hotspot info: {e}")
            return None
    
    def get_species_list_by_region(
        self,
        region_code: str,
        max_results: int = 500
    ) -> List[Dict]:
        """
        Get species list for a region.
        
        Args:
            region_code: eBird region code
            max_results: Maximum number of species
            
        Returns:
            List of species records
        """
        url = f"{self.base_url}/product/spplist/{region_code}"
        params = {'maxResults': max_results}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            species_codes = response.json()
            
            # Convert to more detailed format if possible
            species_list = []
            for code in species_codes:
                species_list.append({
                    'speciesCode': code,
                    'comName': None,  # Would need taxonomy lookup
                    'sciName': None   # Would need taxonomy lookup
                })
            
            logger.info(f"Retrieved {len(species_list)} species from region {region_code}")
            return species_list
            
        except requests.RequestException as e:
            logger.error(f"Error fetching species list: {e}")
            return []
    
    def search_hotspots_by_region(
        self,
        region_code: str,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Search for hotspots in a region.
        
        Args:
            region_code: eBird region code
            max_results: Maximum number of hotspots
            
        Returns:
            List of hotspot records
        """
        url = f"{self.base_url}/ref/hotspot/{region_code}"
        params = {'maxResults': max_results}
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            hotspots = response.json()
            logger.info(f"Found {len(hotspots)} hotspots in region {region_code}")
            
            return hotspots
            
        except requests.RequestException as e:
            logger.error(f"Error searching hotspots: {e}")
            return []
    
    def get_notable_observations(
        self,
        region_code: str,
        days_back: int = 30,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Get notable (rare) observations from a region.
        
        Args:
            region_code: eBird region code
            days_back: Number of days back to search
            max_results: Maximum number of results
            
        Returns:
            List of notable observation records
        """
        if not self.api_key:
            raise ValueError("eBird API key required for notable observations")
        
        url = f"{self.base_url}/data/obs/{region_code}/recent/notable"
        params = {
            'back': days_back,
            'maxResults': max_results
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            observations = response.json()
            logger.info(f"Retrieved {len(observations)} notable observations from {region_code}")
            
            return observations
            
        except requests.RequestException as e:
            logger.error(f"Error fetching notable observations: {e}")
            return []
    
    def validate_region_code(self, region_code: str) -> bool:
        """
        Validate if a region code exists.
        
        Args:
            region_code: eBird region code to validate
            
        Returns:
            True if region code is valid
        """
        url = f"{self.base_url}/ref/region/info/{region_code}"
        
        try:
            response = self.session.get(url, timeout=30)
            return response.status_code == 200
            
        except requests.RequestException:
            return False
    
    def get_api_status(self) -> Dict:
        """
        Get API status information.
        
        Returns:
            Dictionary with API status
        """
        return {
            'has_api_key': bool(self.api_key),
            'base_url': self.base_url,
            'key_preview': f"{self.api_key[:8]}..." if self.api_key else None
        }