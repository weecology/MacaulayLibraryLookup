"""eBird taxonomy handling for species name resolution."""

import logging
import os
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class eBirdTaxonomy:
    """Handle eBird taxonomy data for species name resolution."""
    
    def __init__(self, taxonomy_file: Optional[str] = None):
        """
        Initialize eBird taxonomy handler.
        
        Args:
            taxonomy_file: Path to local taxonomy file (Excel or CSV)
        """
        # Default to Excel file in data directory
        self.taxonomy_file = taxonomy_file or "data/eBird_taxonomy_v2024.xlsx"
        self.taxonomy_data = None
        self._load_taxonomy()
    
    def _load_taxonomy(self) -> None:
        """Load taxonomy data from file."""
        try:
            if not os.path.exists(self.taxonomy_file):
                raise FileNotFoundError(f"Taxonomy file not found: {self.taxonomy_file}")
                
            logger.info(f"Loading taxonomy from {self.taxonomy_file}")
            # Handle both Excel and CSV files
            if self.taxonomy_file.endswith('.xlsx'):
                self.taxonomy_data = pd.read_excel(self.taxonomy_file)
            else:
                self.taxonomy_data = pd.read_csv(self.taxonomy_file)
                
        except Exception as e:
            logger.error(f"Error loading taxonomy: {e}")
            raise
    
    def get_taxon_code_by_common_name(self, common_name: str) -> Optional[str]:
        """
        Get species code by common name.
        
        Args:
            common_name: Common name of the species
            
        Returns:
            Species code or None if not found
        """
        if self.taxonomy_data is None:
            return None
            
        # Try exact match first
        mask = self.taxonomy_data['PRIMARY_COM_NAME'].str.lower() == common_name.lower()
        matches = self.taxonomy_data[mask]
        
        if not matches.empty:
            return matches.iloc[0]['SPECIES_CODE']
        
        # Try partial match
        mask = self.taxonomy_data['PRIMARY_COM_NAME'].str.contains(
            common_name, case=False, na=False
        )
        matches = self.taxonomy_data[mask]
        
        if not matches.empty:
            logger.info(f"Partial match for '{common_name}': {matches.iloc[0]['PRIMARY_COM_NAME']}")
            return matches.iloc[0]['SPECIES_CODE']
        
        logger.warning(f"No match found for common name: {common_name}")
        return None
    
    def get_taxon_code_by_scientific_name(self, scientific_name: str) -> Optional[str]:
        """
        Get species code by scientific name.
        
        Args:
            scientific_name: Scientific name of the species
            
        Returns:
            Species code or None if not found
        """
        if self.taxonomy_data is None:
            return None
            
        # Try exact match
        mask = self.taxonomy_data['SCI_NAME'].str.lower() == scientific_name.lower()
        matches = self.taxonomy_data[mask]
        
        if not matches.empty:
            return matches.iloc[0]['SPECIES_CODE']
        
        # Try partial match
        mask = self.taxonomy_data['SCI_NAME'].str.contains(
            scientific_name, case=False, na=False
        )
        matches = self.taxonomy_data[mask]
        
        if not matches.empty:
            logger.info(f"Partial match for '{scientific_name}': {matches.iloc[0]['SCI_NAME']}")
            return matches.iloc[0]['SPECIES_CODE']
        
        logger.warning(f"No match found for scientific name: {scientific_name}")
        return None
    
    def get_species_info(self, species_code: str) -> Optional[Dict]:
        """
        Get full species information by species code.
        
        Args:
            species_code: eBird species code
            
        Returns:
            Dictionary with species information or None if not found
        """
        if self.taxonomy_data is None:
            return None
            
        mask = self.taxonomy_data['SPECIES_CODE'] == species_code
        matches = self.taxonomy_data[mask]
        
        if not matches.empty:
            row = matches.iloc[0]
            return {
                'species_code': row['SPECIES_CODE'],
                'common_name': row['PRIMARY_COM_NAME'],
                'scientific_name': row['SCI_NAME']
            }
        
        return None
    
    def search_species(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for species by name.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching species
        """
        if self.taxonomy_data is None:
            return []
            
        # Search in both common and scientific names
        common_mask = self.taxonomy_data['PRIMARY_COM_NAME'].str.contains(
            query, case=False, na=False
        )
        sci_mask = self.taxonomy_data['SCI_NAME'].str.contains(
            query, case=False, na=False
        )
        
        matches = self.taxonomy_data[common_mask | sci_mask].head(limit)
        
        results = []
        for _, row in matches.iterrows():
            results.append({
                'species_code': row['SPECIES_CODE'],
                'common_name': row['PRIMARY_COM_NAME'],
                'scientific_name': row['SCI_NAME']
            })
        
        return results
    
    def get_taxonomy_stats(self) -> Dict:
        """
        Get statistics about the taxonomy data.
        
        Returns:
            Dictionary with taxonomy statistics
        """
        if self.taxonomy_data is None:
            return {}
            
        return {
            'total_species': len(self.taxonomy_data),
            'file_path': self.taxonomy_file,
            'columns': list(self.taxonomy_data.columns)
        }