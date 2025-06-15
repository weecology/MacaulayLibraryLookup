# MacaulayLibraryLookup

A Python tool for automating the lookup and retrieval of media catalog IDs from the Cornell Lab of Ornithology's Macaulay Library based on species lists and search criteria.

## 🎯 Overview

This tool helps researchers and bird enthusiasts automate the process of finding audio and visual media from the Macaulay Library by:

1. Taking species lists as input (manual list or from eBird API)
2. Looking up species in the eBird taxonomy
3. Searching the Macaulay Library using customizable filters
4. Extracting catalog IDs and metadata
5. Exporting results to CSV format

## 🔧 Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection (for API access)

### Install from PyPI (once published)
```bash
pip install macaulay-library-lookup
```

### Install from Source
```bash
git clone https://github.com/weecology/MacaulayLibraryLookup.git
cd MacaulayLibraryLookup
pip install -e .
```

## 🚀 Quick Start

### Command Line Interface

```bash
# Search for American Robin recordings in New York during May
macaulay-lookup --species "American Robin" --region "US-NY" --month 5 --media-type audio --tag song

# Use a species list file
macaulay-lookup --species-file species_list.txt --region "US-CA" --output results.csv

# Get species from eBird hotspot
macaulay-lookup --ebird-hotspot "L12345" --month 4,5,6 --media-type photo
```

### Python API

```python
from macaulay_library_lookup import MacaulayLookup

# Initialize the lookup tool
ml = MacaulayLookup()

# Search for a single species
results = ml.search_species(
    common_name="American Robin",
    region="US-NY",
    month=5,
    media_type="audio",
    tag="song"
)

# Search multiple species
species_list = ["American Robin", "Blue Jay", "Cardinal"]
results = ml.search_multiple_species(
    species_list,
    region="US-FL",
    begin_month=3,
    end_month=5
)

# Get species from eBird
results = ml.search_from_ebird_hotspot(
    hotspot_id="L12345",
    days_back=30,
    region="US-CA"
)

# Export to CSV
ml.export_to_csv(results, "macaulay_results.csv")
```

## 📊 Output Format

The tool generates CSV files with the following columns:

- `catalog_id`: Macaulay Library catalog ID
- `species_code`: eBird species code
- `common_name`: Species common name
- `scientific_name`: Species scientific name
- `media_type`: Type of media (audio, photo, video)
- `region`: Geographic region code
- `location`: Recording location
- `date`: Recording date
- `recordist`: Name of recordist
- `url`: Direct URL to the media
- `search_month`: Month(s) used in search
- `search_tag`: Tag used in search (if any)

## 🛠️ Advanced Usage

### Filtering Options

```python
# Advanced filtering
results = ml.search_species(
    common_name="Wood Thrush",
    region="US-NY",
    begin_month=4,
    end_month=8,
    media_type="audio",
    tag="song",
    quality="A",  # High quality recordings only
    background="0",  # No background noise
    recordist="Jane Doe"  # Specific recordist
)
```

### Batch Processing

```python
# Process multiple regions
regions = ["US-NY", "US-CT", "US-MA"]
species = ["Wood Thrush", "Hermit Thrush"]

all_results = []
for region in regions:
    results = ml.search_multiple_species(
        species,
        region=region,
        begin_month=5,
        end_month=7
    )
    all_results.extend(results)

ml.export_to_csv(all_results, "northeast_thrushes.csv")
```

## 🔑 API Keys

Some features require eBird API access:

1. Get an API key from [eBird API](https://ebird.org/api/keygen)
2. Set it as an environment variable:
   ```bash
   export EBIRD_API_KEY="your_api_key_here"
   ```
3. Or pass it directly:
   ```python
   ml = MacaulayLookup(ebird_api_key="your_api_key")
   ```

## 📁 Project Structure

```
MacaulayLibraryLookup/
├── macaulay_library_lookup/
│   ├── __init__.py
│   ├── core.py              # Main lookup functionality
│   ├── ebird_api.py         # eBird API integration
│   ├── taxonomy.py          # eBird taxonomy handling
│   ├── parsers.py           # HTML parsing utilities
│   └── cli.py               # Command line interface
├── tests/
│   ├── test_core.py
│   ├── test_ebird_api.py
│   └── test_taxonomy.py
├── examples/
│   ├── basic_usage.py
│   ├── batch_processing.py
│   └── species_lists/
├── docs/
├── .github/
│   └── workflows/
│       ├── tests.yml
│       └── publish.yml
├── setup.py
├── requirements.txt
├── README.md
└── LICENSE
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=macaulay_library_lookup
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Cornell Lab of Ornithology for the Macaulay Library
- eBird for taxonomy and species data
- The open source community

## 🐛 Issues

If you encounter any issues or have feature requests, please [open an issue](https://github.com/weecology/MacaulayLibraryLookup/issues) on GitHub.

## 📈 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.