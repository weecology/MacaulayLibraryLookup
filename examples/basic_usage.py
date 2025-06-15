#!/usr/bin/env python3
"""
Basic usage examples for MacaulayLibraryLookup.

This script demonstrates how to use the core functionality of the 
MacaulayLibraryLookup package to search for media in the Macaulay Library.
"""

import os
from macaulay_library_lookup import MacaulayLookup

def main():
    """Run basic usage examples."""
    
    print("MacaulayLibraryLookup - Basic Usage Examples")
    print("=" * 50)
    
    # Initialize the lookup tool
    # You can optionally provide an eBird API key for enhanced functionality
    ebird_api_key = os.getenv('EBIRD_API_KEY')
    ml = MacaulayLookup(ebird_api_key=ebird_api_key)
    
    # Example 1: Search for American Robin audio recordings in New York during May
    print("\n1. Searching for American Robin audio in New York during May...")
    results = ml.search_species(
        common_name="American Robin",
        region="US-NY",
        month=5,
        media_type="audio",
        tag="song",
        max_results=5
    )
    
    if results:
        print(f"Found {len(results)} results!")
        for i, result in enumerate(results[:3], 1):
            print(f"  {i}. Catalog ID: {result['catalog_id']}")
            print(f"     URL: {result['url']}")
            print(f"     Location: {result.get('location', 'Unknown')}")
            print()
    else:
        print("No results found.")
    
    # Example 2: Search for multiple species
    print("\n2. Searching for multiple species...")
    species_list = ["Northern Cardinal", "Blue Jay", "American Crow"]
    results = ml.search_multiple_species(
        species_list,
        region="US-FL",
        begin_month=1,
        end_month=3,
        media_type="photo",
        max_results_per_species=3
    )
    
    if results:
        print(f"Found {len(results)} total results for {len(species_list)} species")
        
        # Group by species
        by_species = {}
        for result in results:
            species = result.get('common_name', 'Unknown')
            if species not in by_species:
                by_species[species] = []
            by_species[species].append(result)
        
        for species, species_results in by_species.items():
            print(f"  {species}: {len(species_results)} results")
    else:
        print("No results found.")
    
    # Example 3: Export results to CSV
    if results:
        print("\n3. Exporting results to CSV...")
        ml.export_to_csv(results, "example_results.csv")
        print("Results exported to 'example_results.csv'")
        
        # Show summary statistics
        summary = ml.get_species_summary(results)
        print(f"\nSummary:")
        print(f"  Total records: {summary.get('total_records', 0)}")
        print(f"  Unique species: {summary.get('unique_species', 0)}")
        if summary.get('media_types'):
            print(f"  Media types: {dict(summary['media_types'])}")
    
    # Example 4: Search with scientific name
    print("\n4. Searching by scientific name...")
    results = ml.search_species(
        scientific_name="Turdus migratorius",  # American Robin
        region="US-CA",
        media_type="audio",
        max_results=3
    )
    
    if results:
        print(f"Found {len(results)} results for Turdus migratorius")
        for result in results:
            print(f"  - Catalog ID: {result['catalog_id']}")
    else:
        print("No results found for scientific name search.")
    
    # Example 5: Use eBird hotspot (requires API key)
    if ebird_api_key:
        print("\n5. Searching from eBird hotspot (requires API key)...")
        try:
            # Note: Replace with a real hotspot ID
            hotspot_results = ml.search_from_ebird_hotspot(
                hotspot_id="L159049",  # Example hotspot ID
                days_back=7,
                region="US-NY",
                media_type="audio",
                max_results_per_species=2
            )
            
            if hotspot_results:
                print(f"Found {len(hotspot_results)} results from hotspot")
            else:
                print("No results found from hotspot")
                
        except Exception as e:
            print(f"Error with hotspot search: {e}")
    else:
        print("\n5. Skipping hotspot example (requires EBIRD_API_KEY environment variable)")
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("For more advanced usage, see the other example files and documentation.")


if __name__ == "__main__":
    main()