# Changelog

All notable changes to the MacaulayLibraryLookup project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-20

### Added
- Initial release of MacaulayLibraryLookup
- Core functionality for searching Macaulay Library media
- Support for species name lookup using eBird taxonomy
- Command-line interface with comprehensive options
- Python API for programmatic access
- eBird API integration for hotspot-based searches
- HTML parsing utilities for extracting catalog IDs and metadata
- CSV export functionality with comprehensive metadata
- Rate limiting to respect server resources
- Comprehensive test suite with >90% coverage
- GitHub Actions workflow for CI/CD
- Detailed documentation and usage examples
- Support for multiple search filters:
  - Geographic regions
  - Time periods (months)
  - Media types (audio, photo, video)
  - Quality ratings
  - Background noise levels
  - Media tags (song, call, etc.)
  - Specific recordists

### Features
- **Species Search**: Search by common name, scientific name, or eBird species code
- **Multi-species Processing**: Batch process multiple species with rate limiting
- **eBird Integration**: Get species from hotspots and recent observations
- **Flexible Filtering**: Advanced filtering options for precise searches
- **Export Options**: CSV export with customizable metadata columns
- **Taxonomy Management**: Automatic download and caching of eBird taxonomy
- **Error Handling**: Robust error handling with informative messages
- **Logging**: Comprehensive logging for debugging and monitoring

### Command Line Interface
- `macaulay-lookup search` - Basic species and region searches
- `macaulay-lookup hotspot` - eBird hotspot-based searches
- `macaulay-lookup species-search` - Interactive species lookup
- `macaulay-lookup validate` - CSV file validation
- `macaulay-lookup examples` - Usage examples

### Python API
- `MacaulayLookup` class for core functionality
- `eBirdTaxonomy` class for species name resolution
- `eBirdAPI` class for eBird data integration
- `MacaulayParser` class for HTML parsing

### Dependencies
- requests >= 2.25.0
- beautifulsoup4 >= 4.9.0
- lxml >= 4.6.0
- pandas >= 1.3.0
- click >= 8.0.0
- pydantic >= 1.8.0
- python-dateutil >= 2.8.0

### Documentation
- Comprehensive README with installation and usage instructions
- Example scripts demonstrating basic and advanced usage
- Species list templates for common use cases
- API documentation for all classes and methods

### Testing
- Unit tests for all core functionality
- Integration tests for end-to-end workflows
- Mock tests for external API dependencies
- Coverage reporting with codecov integration

### Infrastructure
- GitHub Actions for automated testing
- Multi-version Python support (3.8-3.12)
- Code quality checks (flake8, black, mypy)
- Automated package publishing workflow

## [Unreleased]

### Planned Features
- Support for additional media metadata extraction
- Caching mechanism for improved performance
- GUI interface for non-technical users
- Integration with additional birding APIs
- Export to additional formats (JSON, Excel)
- Advanced statistical analysis tools
- Docker containerization
- Web service API

### Known Issues
- HTML parsing may be affected by website structure changes
- Rate limiting is conservative and may be adjustable based on usage patterns
- Some metadata fields may not be available for all media types
- Large batch processing may require manual checkpoint management

---

## Contributing

When contributing to this project, please:
1. Update this changelog with your changes
2. Follow semantic versioning principles
3. Include appropriate tests for new features
4. Update documentation as needed

## Release Process

1. Update version numbers in `setup.py` and `__init__.py`
2. Update this changelog with release notes
3. Create a git tag with the version number
4. GitHub Actions will automatically build and publish the release