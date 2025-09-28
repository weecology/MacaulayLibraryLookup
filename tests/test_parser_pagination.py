"""Tests for parser pagination functionality."""

import pytest
from bs4 import BeautifulSoup

from macaulay_library_lookup.parsers import MacaulayParser


class TestMacaulayParserPagination:
    """Test cases for MacaulayParser pagination detection."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MacaulayParser()
        
    def test_detect_pagination_info_no_pagination(self):
        """Test pagination detection with no pagination elements."""
        html = '<html><body><div>No pagination here</div></body></html>'
        soup = BeautifulSoup(html, 'lxml')
        
        pagination_info = self.parser.detect_pagination_info(soup)
        
        assert pagination_info['has_next_page'] is False
        assert pagination_info['total_results'] is None
        assert pagination_info['current_page'] is None
        assert pagination_info['total_pages'] is None
        
    def test_detect_pagination_info_with_next_link(self):
        """Test pagination detection with next link."""
        html = '''
        <html><body>
            <div class="pagination">
                <a href="?page=1">1</a>
                <a href="?page=2">2</a>
                <a href="?page=3">3</a>
                <a href="?page=2">Next</a>
            </div>
        </body></html>
        '''
        soup = BeautifulSoup(html, 'lxml')
        
        pagination_info = self.parser.detect_pagination_info(soup)
        
        assert pagination_info['has_next_page'] is True
        assert pagination_info['total_pages'] == 3
        
    def test_detect_pagination_info_with_more_button(self):
        """Test pagination detection with 'more' button."""
        html = '''
        <html><body>
            <div class="pager">
                <button>Load More</button>
            </div>
        </body></html>
        '''
        soup = BeautifulSoup(html, 'lxml')
        
        pagination_info = self.parser.detect_pagination_info(soup)
        
        assert pagination_info['has_next_page'] is True
        
    def test_detect_pagination_info_with_result_count(self):
        """Test pagination detection with result count text."""
        html = '''
        <html><body>
            <div>Showing 1-50 of 342 results</div>
        </body></html>
        '''
        soup = BeautifulSoup(html, 'lxml')
        
        pagination_info = self.parser.detect_pagination_info(soup)
        
        assert pagination_info['total_results'] == 342
        
    def test_detect_pagination_info_various_result_formats(self):
        """Test pagination detection with various result count formats."""
        test_cases = [
            ('150 of 500 results', 500),
            ('showing 25 of 200 results', 200),
            ('300 results found', None),  # This pattern doesn't capture total
            ('1-25 of 100 results', 100)
        ]
        
        for text, expected_total in test_cases:
            html = f'<html><body><div>{text}</div></body></html>'
            soup = BeautifulSoup(html, 'lxml')
            
            pagination_info = self.parser.detect_pagination_info(soup)
            assert pagination_info['total_results'] == expected_total
        
    def test_detect_pagination_info_aria_navigation(self):
        """Test pagination detection with ARIA navigation."""
        html = '''
        <html><body>
            <nav aria-label="pagination navigation">
                <a href="?page=2">></a>
            </nav>
        </body></html>
        '''
        soup = BeautifulSoup(html, 'lxml')
        
        pagination_info = self.parser.detect_pagination_info(soup)
        
        assert pagination_info['has_next_page'] is True