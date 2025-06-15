"""MacaulayLibraryLookup - A tool for automating Macaulay Library media lookups."""

__version__ = "1.0.0"
__author__ = "Weecology"
__email__ = "weecology@weecology.org"

from .core import MacaulayLookup
from .taxonomy import eBirdTaxonomy
from .ebird_api import eBirdAPI

__all__ = [
    "MacaulayLookup",
    "eBirdTaxonomy", 
    "eBirdAPI",
]