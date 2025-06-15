"""Core functionality for Macaulay Library lookups."""

import csv
import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode, urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .ebird_api import eBirdAPI
from .parsers import MacaulayParser
from .taxonomy import eBirdTaxonomy

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MacaulayLookup:
    """Main class for looking up media in the Macaulay Library."""

    def __init__(self, ebird_api_key: Optional[str] = None, rate_limit: float = 1.0):
        """
        Initialize MacaulayLookup.
        
        Args:
            ebird_api_key: eBird API key for enhanced functionality
            rate_limit: Rate limit between requests in seconds
        """
        self.base_url = "https://media.ebird.org/catalog"
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.taxonomy = eBirdTaxonomy()
        self.ebird_api = eBirdAPI(api_key=ebird_api_key) if ebird_api_key else None
        self.parser = MacaulayParser()
        
    def search_species(
        self,
        common_name: Optional[str] = None,
        scientific_name: Optional[str] = None,
        taxon_code: Optional[str] = None,
        region: Optional[str] = None,
        begin_month: Optional[int] = None,
        end_month: Optional[int] = None,
        month: Optional[int] = None,
        media_type: str = "audio",
        tag: Optional[str] = None,
        quality: Optional[str] = None,
        background: Optional[str] = None,
        recordist: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict]:
        """
        Search for media of a single species.
        
        Args:
            common_name: Common name of the species
            scientific_name: Scientific name of the species
            taxon_code: eBird species code
            region: Geographic region code (e.g., 'US-NY')
            begin_month: Starting month (1-12)
            end_month: Ending month (1-12)
            month: Single month (alternative to begin/end)
            media_type: Type of media ('audio', 'photo', 'video')
            tag: Media tag (e.g., 'song', 'call')
            quality: Quality rating ('A', 'B', 'C', 'D', 'E')
            background: Background noise level ('0', '1', '2', '3', '4')
            recordist: Name of recordist
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing media information
        """
        # Get taxon code if not provided
        if not taxon_code:
            if common_name:
                taxon_code = self.taxonomy.get_taxon_code_by_common_name(common_name)
            elif scientific_name:
                taxon_code = self.taxonomy.get_taxon_code_by_scientific_name(scientific_name)
            
            if not taxon_code:
                logger.warning(f"Could not find taxon code for species: {common_name or scientific_name}")
                return []
        
        # Handle month parameters
        if month is not None:
            begin_month = end_month = month
            
        # Build search parameters
        params = {
            'view': 'list',
            'all': 'true',
            'taxonCode': taxon_code,
            'mediaType': media_type
        }
        
        if region:
            params['regionCode'] = region
        if begin_month:
            params['beginMonth'] = begin_month
        if end_month:
            params['endMonth'] = end_month
        if tag:
            params['tag'] = tag
        if quality:
            params['quality'] = quality
        if background:
            params['background'] = background
        if recordist:
            params['recordist'] = recordist
            
        return self._fetch_media_data(params, max_results)
    
    def search_multiple_species(
        self,
        species_list: List[str],
        region: Optional[str] = None,
        begin_month: Optional[int] = None,
        end_month: Optional[int] = None,
        media_type: str = "audio",
        tag: Optional[str] = None,
        max_results_per_species: int = 50
    ) -> List[Dict]:
        """
        Search for media of multiple species.
        
        Args:
            species_list: List of species common names
            region: Geographic region code
            begin_month: Starting month
            end_month: Ending month
            media_type: Type of media
            tag: Media tag
            max_results_per_species: Max results per species
            
        Returns:
            Combined list of media records for all species
        """
        all_results = []
        
        for species in species_list:
            logger.info(f"Searching for {species}...")
            results = self.search_species(
                common_name=species,
                region=region,
                begin_month=begin_month,
                end_month=end_month,
                media_type=media_type,
                tag=tag,
                max_results=max_results_per_species
            )
            all_results.extend(results)
            
            # Rate limiting
            time.sleep(self.rate_limit)
            
        return all_results
    
    def search_from_ebird_hotspot(
        self,
        hotspot_id: str,
        days_back: int = 30,
        region: Optional[str] = None,
        begin_month: Optional[int] = None,
        end_month: Optional[int] = None,
        media_type: str = "audio",
        max_results_per_species: int = 20
    ) -> List[Dict]:
        """
        Get species from eBird hotspot and search for their media.
        
        Args:
            hotspot_id: eBird hotspot identifier
            days_back: Number of days back to search
            region: Geographic region for media search
            begin_month: Starting month for media search
            end_month: Ending month for media search
            media_type: Type of media
            max_results_per_species: Max results per species
            
        Returns:
            List of media records for species found at hotspot
        """
        if not self.ebird_api:
            raise ValueError("eBird API key required for hotspot searches")
            
        # Get species from hotspot
        species_list = self.ebird_api.get_recent_observations_by_hotspot(
            hotspot_id, days_back
        )
        
        if not species_list:
            logger.warning(f"No species found for hotspot {hotspot_id}")
            return []
        
        # Extract common names
        common_names = [obs['comName'] for obs in species_list]
        
        return self.search_multiple_species(
            common_names,
            region=region,
            begin_month=begin_month,
            end_month=end_month,
            media_type=media_type,
            max_results_per_species=max_results_per_species
        )
    
    def _fetch_media_data(self, params: Dict, max_results: int) -> List[Dict]:
        """
        Fetch media data from Macaulay Library.
        
        Args:
            params: Search parameters
            max_results: Maximum number of results
            
        Returns:
            List of media records
        """
        url = f"{self.base_url}?{urlencode(params)}"
        logger.info(f"Fetching: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            media_records = self.parser.parse_catalog_page(soup, params)
            
            # Limit results
            return media_records[:max_results]
            
        except requests.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            return []
    
    def export_to_csv(self, results: List[Dict], filename: str) -> None:
        """
        Export results to CSV file.
        
        Args:
            results: List of media records
            filename: Output filename
        """
        if not results:
            logger.warning("No results to export")
            return
            
        df = pd.DataFrame(results)
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(results)} records to {filename}")
    
    def get_species_summary(self, results: List[Dict]) -> Dict:
        """
        Get summary statistics for search results.
        
        Args:
            results: List of media records
            
        Returns:
            Dictionary with summary statistics
        """
        if not results:
            return {}
            
        df = pd.DataFrame(results)
        
        summary = {
            'total_records': len(df),
            'unique_species': df['common_name'].nunique() if 'common_name' in df else 0,
            'media_types': dict(df['media_type'].value_counts()) if 'media_type' in df else {},
            'regions': dict(df['region'].value_counts()) if 'region' in df else {},
            'date_range': {
                'earliest': df['date'].min() if 'date' in df else None,
                'latest': df['date'].max() if 'date' in df else None
            }
        }
        
        return summary