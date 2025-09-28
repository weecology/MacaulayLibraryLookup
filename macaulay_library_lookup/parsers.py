"""HTML parsing utilities for Macaulay Library pages."""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class MacaulayParser:
    """Parse Macaulay Library HTML pages to extract media information."""
    
    def __init__(self):
        """Initialize the parser."""
        self.catalog_id_pattern = re.compile(r'/asset/(\d+)')
        self.media_url_pattern = re.compile(r'https?://macaulaylibrary\.org/asset/(\d+)')
    
    def parse_catalog_page(self, soup: BeautifulSoup, search_params: Dict) -> List[Dict]:
        """
        Parse a catalog search results page.
        
        Args:
            soup: BeautifulSoup object of the page
            search_params: Original search parameters used
            
        Returns:
            List of media record dictionaries
        """
        media_records = []
        
        # Look for media items in the page
        # The structure may vary, so we'll try multiple approaches
        
        # Method 1: Look for direct links to assets
        asset_links = soup.find_all('a', href=self.catalog_id_pattern)
        for link in asset_links:
            catalog_id = self.catalog_id_pattern.search(link['href']).group(1)
            record = self._extract_record_from_link(link, catalog_id, search_params)
            if record:
                media_records.append(record)
        
        # Method 2: Look for data embedded in script tags or data attributes
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string:
                records = self._extract_records_from_script(script.string, search_params)
                media_records.extend(records)
        
        # Method 3: Look for structured data in specific containers
        containers = soup.find_all(['div', 'article'], class_=re.compile(r'(media|asset|result)'))
        for container in containers:
            record = self._extract_record_from_container(container, search_params)
            if record:
                media_records.append(record)
        
        # Remove duplicates based on catalog_id
        seen_ids = set()
        unique_records = []
        for record in media_records:
            if record['catalog_id'] not in seen_ids:
                seen_ids.add(record['catalog_id'])
                unique_records.append(record)
        
        logger.info(f"Extracted {len(unique_records)} unique media records")
        return unique_records
    
    def _extract_record_from_link(self, link: Tag, catalog_id: str, search_params: Dict) -> Optional[Dict]:
        """
        Extract record information from a link element.
        
        Args:
            link: BeautifulSoup link element
            catalog_id: Extracted catalog ID
            search_params: Search parameters
            
        Returns:
            Media record dictionary or None
        """
        try:
            # Get the parent container for more context
            container = link.find_parent(['div', 'article', 'li'])
            
            record = {
                'catalog_id': catalog_id,
                'url': f"https://macaulaylibrary.org/asset/{catalog_id}",
                'media_type': search_params.get('mediaType', 'unknown'),
                'region': search_params.get('regionCode', ''),
                'search_month': search_params.get('beginMonth', ''),
                'search_tag': search_params.get('tag', ''),
                'species_code': search_params.get('taxonCode', ''),
                'common_name': '',
                'scientific_name': '',
                'location': '',
                'date': '',
                'recordist': ''
            }
            
            if container:
                # Try to extract additional information from the container
                record.update(self._extract_metadata_from_container(container))
            
            return record
            
        except Exception as e:
            logger.warning(f"Error extracting record from link: {e}")
            return None
    
    def _extract_records_from_script(self, script_content: str, search_params: Dict) -> List[Dict]:
        """
        Extract records from JavaScript content.
        
        Args:
            script_content: JavaScript content as string
            search_params: Search parameters
            
        Returns:
            List of media records
        """
        records = []
        
        # Look for catalog IDs in various formats
        catalog_patterns = [
            r'"assetId":\s*"?(\d+)"?',
            r'"catalogId":\s*"?(\d+)"?',
            r'"id":\s*"?(\d+)"?',
            r'/asset/(\d+)',
            r'macaulaylibrary\.org/asset/(\d+)'
        ]
        
        for pattern in catalog_patterns:
            matches = re.findall(pattern, script_content)
            for match in matches:
                if match.isdigit() and len(match) >= 6:  # Reasonable catalog ID length
                    record = {
                        'catalog_id': match,
                        'url': f"https://macaulaylibrary.org/asset/{match}",
                        'media_type': search_params.get('mediaType', 'unknown'),
                        'region': search_params.get('regionCode', ''),
                        'search_month': search_params.get('beginMonth', ''),
                        'search_tag': search_params.get('tag', ''),
                        'species_code': search_params.get('taxonCode', ''),
                        'common_name': '',
                        'scientific_name': '',
                        'location': '',
                        'date': '',
                        'recordist': ''
                    }
                    records.append(record)
        
        return records
    
    def _extract_record_from_container(self, container: Tag, search_params: Dict) -> Optional[Dict]:
        """
        Extract record from a container element.
        
        Args:
            container: BeautifulSoup container element
            search_params: Search parameters
            
        Returns:
            Media record dictionary or None
        """
        # Look for catalog ID in various places
        catalog_id = None
        
        # Check data attributes
        if container.get('data-asset-id'):
            catalog_id = container['data-asset-id']
        elif container.get('data-catalog-id'):
            catalog_id = container['data-catalog-id']
        
        # Check for links within the container
        if not catalog_id:
            links = container.find_all('a', href=self.catalog_id_pattern)
            if links:
                match = self.catalog_id_pattern.search(links[0]['href'])
                if match:
                    catalog_id = match.group(1)
        
        if not catalog_id:
            return None
        
        record = {
            'catalog_id': catalog_id,
            'url': f"https://macaulaylibrary.org/asset/{catalog_id}",
            'media_type': search_params.get('mediaType', 'unknown'),
            'region': search_params.get('regionCode', ''),
            'search_month': search_params.get('beginMonth', ''),
            'search_tag': search_params.get('tag', ''),
            'species_code': search_params.get('taxonCode', ''),
            'common_name': '',
            'scientific_name': '',
            'location': '',
            'date': '',
            'recordist': ''
        }
        
        # Extract additional metadata
        record.update(self._extract_metadata_from_container(container))
        
        return record
    
    def _extract_metadata_from_container(self, container: Tag) -> Dict:
        """
        Extract metadata from a container element.
        
        Args:
            container: BeautifulSoup container element
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        
        # Try to find species name
        species_elements = container.find_all(text=re.compile(r'[A-Z][a-z]+ [a-z]+'))
        for text in species_elements:
            if len(text.strip().split()) >= 2:
                metadata['common_name'] = text.strip()
                break
        
        # Try to find location
        location_patterns = [
            r'class.*location',
            r'class.*place',
            r'class.*locale'
        ]
        for pattern in location_patterns:
            location_elem = container.find(attrs={'class': re.compile(pattern, re.I)})
            if location_elem:
                metadata['location'] = location_elem.get_text(strip=True)
                break
        
        # Try to find date
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b[A-Z][a-z]+ \d{1,2}, \d{4}\b'
        ]
        container_text = container.get_text()
        for pattern in date_patterns:
            match = re.search(pattern, container_text)
            if match:
                metadata['date'] = match.group()
                break
        
        # Try to find recordist
        recordist_patterns = [
            r'by\s+([A-Z][a-z]+ [A-Z][a-z]+)',
            r'recordist[:\s]+([A-Z][a-z]+ [A-Z][a-z]+)',
            r'recorded by\s+([A-Z][a-z]+ [A-Z][a-z]+)'
        ]
        for pattern in recordist_patterns:
            match = re.search(pattern, container_text, re.I)
            if match:
                metadata['recordist'] = match.group(1)
                break
        
        return metadata
    
    def parse_asset_page(self, soup: BeautifulSoup, catalog_id: str) -> Optional[Dict]:
        """
        Parse an individual asset page for detailed information.
        
        Args:
            soup: BeautifulSoup object of the asset page
            catalog_id: Catalog ID of the asset
            
        Returns:
            Detailed asset information dictionary
        """
        try:
            record = {
                'catalog_id': catalog_id,
                'url': f"https://macaulaylibrary.org/asset/{catalog_id}",
                'common_name': '',
                'scientific_name': '',
                'media_type': '',
                'location': '',
                'date': '',
                'recordist': '',
                'quality': '',
                'tags': [],
                'description': ''
            }
            
            # Extract species information
            species_elem = soup.find('h1') or soup.find(class_=re.compile(r'species|title'))
            if species_elem:
                record['common_name'] = species_elem.get_text(strip=True)
            
            # Extract scientific name
            sci_name_elem = soup.find(class_=re.compile(r'scientific|latin'))
            if sci_name_elem:
                record['scientific_name'] = sci_name_elem.get_text(strip=True)
            
            # Extract metadata from structured data
            meta_elements = soup.find_all(['meta', 'span', 'div'], 
                                        attrs={'property': re.compile(r'.*')})
            for elem in meta_elements:
                prop = elem.get('property', '').lower()
                if 'location' in prop:
                    record['location'] = elem.get('content', elem.get_text(strip=True))
                elif 'date' in prop:
                    record['date'] = elem.get('content', elem.get_text(strip=True))
                elif 'creator' in prop or 'author' in prop:
                    record['recordist'] = elem.get('content', elem.get_text(strip=True))
            
            return record
            
        except Exception as e:
            logger.error(f"Error parsing asset page: {e}")
            return None
    
    def extract_catalog_ids_from_url(self, url: str) -> List[str]:
        """
        Extract catalog IDs from a URL.
        
        Args:
            url: URL to extract catalog IDs from
            
        Returns:
            List of catalog IDs found in the URL
        """
        matches = self.media_url_pattern.findall(url)
        return matches

    def detect_pagination_info(self, soup: BeautifulSoup) -> Dict:
        """
        Detect pagination information from a catalog page.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Dictionary with pagination information
        """
        pagination_info = {
            'has_next_page': False,
            'total_results': None,
            'current_page': None,
            'total_pages': None,
            'results_per_page': None
        }
        
        # Look for common pagination indicators
        pagination_patterns = [
            # Common pagination class names
            {'class': re.compile(r'pagination', re.I)},
            {'class': re.compile(r'pager', re.I)},
            {'class': re.compile(r'page-nav', re.I)},
            # Common pagination element types
            {'role': 'navigation'},
            {'aria-label': re.compile(r'pagination', re.I)}
        ]
        
        for pattern in pagination_patterns:
            pagination_elem = soup.find(attrs=pattern)
            if pagination_elem:
                # Look for "next" links or buttons
                next_indicators = pagination_elem.find_all(['a', 'button'], 
                    string=re.compile(r'next|more|\>', re.I))
                if next_indicators:
                    pagination_info['has_next_page'] = True
                
                # Look for page numbers
                page_links = pagination_elem.find_all('a', string=re.compile(r'^\d+$'))
                if page_links:
                    page_numbers = [int(link.get_text()) for link in page_links]
                    pagination_info['total_pages'] = max(page_numbers) if page_numbers else None
                
                break
        
        # Look for result count indicators
        result_count_patterns = [
            r'(\d+)\s*(?:of\s*(\d+))?\s*results?',
            r'showing\s*(\d+)\s*(?:of\s*(\d+))?\s*results?',
            r'(\d+)\s*-\s*(\d+)\s*of\s*(\d+)\s*results?'
        ]
        
        page_text = soup.get_text()
        for pattern in result_count_patterns:
            match = re.search(pattern, page_text, re.I)
            if match:
                groups = match.groups()
                if len(groups) >= 2 and groups[1]:
                    pagination_info['total_results'] = int(groups[1])
                break
        
        return pagination_info