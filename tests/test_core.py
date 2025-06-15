"""Tests for core MacaulayLookup functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from bs4 import BeautifulSoup

from macaulay_library_lookup.core import MacaulayLookup


class TestMacaulayLookup:
    """Test cases for MacaulayLookup class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.ml = MacaulayLookup()
        
    def test_initialization(self):
        """Test MacaulayLookup initialization."""
        assert self.ml.base_url == "https://media.ebird.org/catalog"
        assert self.ml.rate_limit == 1.0
        assert self.ml.session is not None
        assert self.ml.taxonomy is not None
        assert self.ml.parser is not None
        
    def test_initialization_with_api_key(self):
        """Test initialization with eBird API key."""
        ml = MacaulayLookup(ebird_api_key="test_key")
        assert ml.ebird_api is not None
        
    @patch('macaulay_library_lookup.core.requests.Session.get')
    def test_fetch_media_data_success(self, mock_get):
        """Test successful media data fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.content = b'<html><body><a href="/asset/123456">Test</a></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        params = {'taxonCode': 'amerob', 'mediaType': 'audio'}
        results = self.ml._fetch_media_data(params, 100)
        
        # Verify request was made
        mock_get.assert_called_once()
        assert isinstance(results, list)
        
    @patch('macaulay_library_lookup.core.requests.Session.get')
    def test_fetch_media_data_error(self, mock_get):
        """Test media data fetching with network error."""
        mock_get.side_effect = requests.RequestException("Network error")
        
        params = {'taxonCode': 'amerob', 'mediaType': 'audio'}
        results = self.ml._fetch_media_data(params, 100)
        
        assert results == []
        
    def test_search_species_no_taxon_code(self):
        """Test species search without valid taxon code."""
        with patch.object(self.ml.taxonomy, 'get_taxon_code_by_common_name', return_value=None):
            results = self.ml.search_species(common_name="Invalid Species")
            assert results == []
            
    @patch.object(MacaulayLookup, '_fetch_media_data')
    def test_search_species_with_common_name(self, mock_fetch):
        """Test species search with common name."""
        mock_fetch.return_value = [{'catalog_id': '123456'}]
        
        with patch.object(self.ml.taxonomy, 'get_taxon_code_by_common_name', return_value='amerob'):
            results = self.ml.search_species(common_name="American Robin")
            
        assert len(results) == 1
        assert results[0]['catalog_id'] == '123456'
        mock_fetch.assert_called_once()
        
    @patch.object(MacaulayLookup, '_fetch_media_data')
    def test_search_species_with_month_param(self, mock_fetch):
        """Test species search with month parameter."""
        mock_fetch.return_value = []
        
        with patch.object(self.ml.taxonomy, 'get_taxon_code_by_common_name', return_value='amerob'):
            self.ml.search_species(common_name="American Robin", month=5)
            
        # Verify that month was converted to begin_month and end_month
        call_args = mock_fetch.call_args[0][0]  # Get the params argument
        assert call_args['beginMonth'] == 5
        assert call_args['endMonth'] == 5
        
    @patch.object(MacaulayLookup, 'search_species')
    @patch('time.sleep')
    def test_search_multiple_species(self, mock_sleep, mock_search):
        """Test searching multiple species."""
        mock_search.return_value = [{'catalog_id': '123456'}]
        
        species_list = ["American Robin", "Blue Jay"]
        results = self.ml.search_multiple_species(species_list)
        
        # Should be called twice
        assert mock_search.call_count == 2
        assert len(results) == 2
        # Should have rate limiting
        assert mock_sleep.call_count == 2
        
    def test_search_from_ebird_hotspot_no_api_key(self):
        """Test hotspot search without API key."""
        with pytest.raises(ValueError, match="eBird API key required"):
            self.ml.search_from_ebird_hotspot("L12345")
            
    def test_export_to_csv_no_results(self):
        """Test CSV export with no results."""
        with patch('macaulay_library_lookup.core.logger') as mock_logger:
            self.ml.export_to_csv([], "test.csv")
            mock_logger.warning.assert_called_with("No results to export")
            
    @patch('pandas.DataFrame.to_csv')
    def test_export_to_csv_with_results(self, mock_to_csv):
        """Test CSV export with results."""
        results = [{'catalog_id': '123456', 'species': 'American Robin'}]
        
        self.ml.export_to_csv(results, "test.csv")
        
        mock_to_csv.assert_called_once_with("test.csv", index=False)
        
    def test_get_species_summary_empty(self):
        """Test species summary with empty results."""
        summary = self.ml.get_species_summary([])
        assert summary == {}
        
    def test_get_species_summary_with_data(self):
        """Test species summary with data."""
        results = [
            {'catalog_id': '123456', 'common_name': 'American Robin', 'media_type': 'audio'},
            {'catalog_id': '789012', 'common_name': 'Blue Jay', 'media_type': 'audio'},
            {'catalog_id': '345678', 'common_name': 'American Robin', 'media_type': 'photo'}
        ]
        
        summary = self.ml.get_species_summary(results)
        
        assert summary['total_records'] == 3
        assert summary['unique_species'] == 2
        assert 'media_types' in summary
        assert 'date_range' in summary