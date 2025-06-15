"""Tests for eBird taxonomy functionality."""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, mock_open
import requests

from macaulay_library_lookup.taxonomy import eBirdTaxonomy


class TesteBirdTaxonomy:
    """Test cases for eBirdTaxonomy class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create taxonomy with mock data to avoid downloading
        with patch.object(eBirdTaxonomy, '_load_taxonomy'):
            self.taxonomy = eBirdTaxonomy()
            
        # Set up mock taxonomy data
        self.taxonomy.taxonomy_data = pd.DataFrame([
            {"SPECIES_CODE": "amerob", "PRIMARY_COM_NAME": "American Robin", 
             "SCI_NAME": "Turdus migratorius"},
            {"SPECIES_CODE": "norcar", "PRIMARY_COM_NAME": "Northern Cardinal", 
             "SCI_NAME": "Cardinalis cardinalis"},
            {"SPECIES_CODE": "blujay", "PRIMARY_COM_NAME": "Blue Jay", 
             "SCI_NAME": "Cyanocitta cristata"}
        ])
        
    def test_initialization(self):
        """Test taxonomy initialization."""
        assert self.taxonomy.taxonomy_url is not None
        assert self.taxonomy.taxonomy_file == "ebird_taxonomy.csv"
        
    def test_get_taxon_code_by_common_name_exact_match(self):
        """Test getting taxon code by exact common name match."""
        code = self.taxonomy.get_taxon_code_by_common_name("American Robin")
        assert code == "amerob"
        
    def test_get_taxon_code_by_common_name_case_insensitive(self):
        """Test getting taxon code by common name (case insensitive)."""
        code = self.taxonomy.get_taxon_code_by_common_name("american robin")
        assert code == "amerob"
        
    def test_get_taxon_code_by_common_name_partial_match(self):
        """Test getting taxon code by partial common name match."""
        code = self.taxonomy.get_taxon_code_by_common_name("Robin")
        assert code == "amerob"
        
    def test_get_taxon_code_by_common_name_no_match(self):
        """Test getting taxon code when no match found."""
        code = self.taxonomy.get_taxon_code_by_common_name("Nonexistent Bird")
        assert code is None
        
    def test_get_taxon_code_by_scientific_name_exact_match(self):
        """Test getting taxon code by exact scientific name match."""
        code = self.taxonomy.get_taxon_code_by_scientific_name("Turdus migratorius")
        assert code == "amerob"
        
    def test_get_taxon_code_by_scientific_name_case_insensitive(self):
        """Test getting taxon code by scientific name (case insensitive)."""
        code = self.taxonomy.get_taxon_code_by_scientific_name("turdus migratorius")
        assert code == "amerob"
        
    def test_get_taxon_code_by_scientific_name_partial_match(self):
        """Test getting taxon code by partial scientific name match."""
        code = self.taxonomy.get_taxon_code_by_scientific_name("Turdus")
        assert code == "amerob"
        
    def test_get_taxon_code_by_scientific_name_no_match(self):
        """Test getting taxon code when no scientific name match found."""
        code = self.taxonomy.get_taxon_code_by_scientific_name("Nonexistent species")
        assert code is None
        
    def test_get_species_info_found(self):
        """Test getting species info when species exists."""
        info = self.taxonomy.get_species_info("amerob")
        
        assert info is not None
        assert info['species_code'] == "amerob"
        assert info['common_name'] == "American Robin"
        assert info['scientific_name'] == "Turdus migratorius"
        
    def test_get_species_info_not_found(self):
        """Test getting species info when species doesn't exist."""
        info = self.taxonomy.get_species_info("nonexistent")
        assert info is None
        
    def test_search_species(self):
        """Test species search functionality."""
        results = self.taxonomy.search_species("Robin", limit=5)
        
        assert len(results) == 1
        assert results[0]['common_name'] == "American Robin"
        assert results[0]['species_code'] == "amerob"
        
    def test_search_species_multiple_matches(self):
        """Test species search with multiple matches."""
        results = self.taxonomy.search_species("Cardinal", limit=5)
        
        assert len(results) == 1
        assert results[0]['common_name'] == "Northern Cardinal"
        
    def test_search_species_no_matches(self):
        """Test species search with no matches."""
        results = self.taxonomy.search_species("Nonexistent", limit=5)
        assert len(results) == 0
        
    def test_get_taxonomy_stats(self):
        """Test getting taxonomy statistics."""
        stats = self.taxonomy.get_taxonomy_stats()
        
        assert stats['total_species'] == 3
        assert stats['file_path'] == "ebird_taxonomy.csv"
        assert 'columns' in stats
        
    def test_get_taxonomy_stats_no_data(self):
        """Test getting taxonomy statistics with no data."""
        self.taxonomy.taxonomy_data = None
        stats = self.taxonomy.get_taxonomy_stats()
        assert stats == {}
        
    @patch('os.path.exists', return_value=True)
    @patch('pandas.read_csv')
    def test_load_taxonomy_from_file(self, mock_read_csv, mock_exists):
        """Test loading taxonomy from existing file."""
        mock_df = pd.DataFrame([{"SPECIES_CODE": "test", "PRIMARY_COM_NAME": "Test"}])
        mock_read_csv.return_value = mock_df
        
        taxonomy = eBirdTaxonomy()
        
        mock_read_csv.assert_called_once_with("ebird_taxonomy.csv")
        assert taxonomy.taxonomy_data is not None
        
    @patch('os.path.exists', return_value=False)
    @patch.object(eBirdTaxonomy, '_download_taxonomy')
    def test_load_taxonomy_download(self, mock_download, mock_exists):
        """Test loading taxonomy by downloading."""
        taxonomy = eBirdTaxonomy()
        mock_download.assert_called_once()
        
    @patch('requests.get')
    @patch('builtins.open', new_callable=mock_open)
    @patch('pandas.read_csv')
    def test_download_taxonomy_success(self, mock_read_csv, mock_file, mock_get):
        """Test successful taxonomy download."""
        # Mock successful download
        mock_response = Mock()
        mock_response.content = b"test,data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        mock_df = pd.DataFrame([{"SPECIES_CODE": "test"}])
        mock_read_csv.return_value = mock_df
        
        with patch.object(eBirdTaxonomy, '_load_taxonomy'):
            taxonomy = eBirdTaxonomy()
            
        taxonomy._download_taxonomy()
        
        mock_get.assert_called_once()
        mock_file.assert_called_once_with("ebird_taxonomy.csv", 'wb')
        
    @patch('requests.get')
    @patch.object(eBirdTaxonomy, '_create_fallback_taxonomy')
    def test_download_taxonomy_failure(self, mock_fallback, mock_get):
        """Test taxonomy download failure."""
        mock_get.side_effect = requests.RequestException("Download failed")
        
        with patch.object(eBirdTaxonomy, '_load_taxonomy'):
            taxonomy = eBirdTaxonomy()
            
        taxonomy._download_taxonomy()
        
        mock_fallback.assert_called_once()
        
    def test_create_fallback_taxonomy(self):
        """Test creation of fallback taxonomy."""
        with patch.object(eBirdTaxonomy, '_load_taxonomy'):
            taxonomy = eBirdTaxonomy()
            
        taxonomy._create_fallback_taxonomy()
        
        assert taxonomy.taxonomy_data is not None
        assert len(taxonomy.taxonomy_data) == 10  # Should have 10 fallback species
        assert "amerob" in taxonomy.taxonomy_data['SPECIES_CODE'].values