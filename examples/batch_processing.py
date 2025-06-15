#!/usr/bin/env python3
"""
Batch processing example for MacaulayLibraryLookup.

This script demonstrates how to perform large-scale batch processing
of multiple species across different regions and time periods.
"""

import os
import time
from datetime import datetime
from macaulay_library_lookup import MacaulayLookup

def main():
    """Run batch processing example."""
    
    print("MacaulayLibraryLookup - Batch Processing Example")
    print("=" * 50)
    
    # Initialize the lookup tool with rate limiting
    ebird_api_key = os.getenv('EBIRD_API_KEY')
    ml = MacaulayLookup(ebird_api_key=ebird_api_key, rate_limit=2.0)  # 2 second delay
    
    # Define target species
    target_species = [
        "Wood Thrush",
        "Hermit Thrush", 
        "Veery",
        "Swainson's Thrush"
    ]
    
    # Define regions of interest
    regions = [
        ("US-NY", "New York"),
        ("US-CT", "Connecticut"),
        ("US-MA", "Massachusetts"),
        ("US-VT", "Vermont")
    ]
    
    # Define search parameters
    search_params = {
        "begin_month": 5,      # May
        "end_month": 7,        # July
        "media_type": "audio",
        "tag": "song",
        "max_results_per_species": 10
    }
    
    print(f"Processing {len(target_species)} species across {len(regions)} regions...")
    print(f"Search period: Months {search_params['begin_month']}-{search_params['end_month']}")
    print(f"Media type: {search_params['media_type']}")
    print()
    
    all_results = []
    total_searches = len(target_species) * len(regions)
    current_search = 0
    
    start_time = datetime.now()
    
    # Process each region
    for region_code, region_name in regions:
        print(f"Processing {region_name} ({region_code})...")
        
        region_results = []
        
        # Process each species in the region
        for species in target_species:
            current_search += 1
            progress = (current_search / total_searches) * 100
            
            print(f"  [{current_search}/{total_searches}] ({progress:.1f}%) Searching for {species}...")
            
            try:
                # Search for this species in this region
                results = ml.search_species(
                    common_name=species,
                    region=region_code,
                    begin_month=search_params["begin_month"],
                    end_month=search_params["end_month"],
                    media_type=search_params["media_type"],
                    tag=search_params["tag"],
                    max_results=search_params["max_results_per_species"]
                )
                
                # Add region name to results for easier analysis
                for result in results:
                    result['region_name'] = region_name
                
                region_results.extend(results)
                all_results.extend(results)
                
                print(f"    Found {len(results)} results")
                
            except Exception as e:
                print(f"    Error searching for {species}: {e}")
                continue
        
        # Save intermediate results for this region
        if region_results:
            filename = f"thrush_audio_{region_code.lower().replace('-', '_')}.csv"
            ml.export_to_csv(region_results, filename)
            print(f"  Saved {len(region_results)} results to {filename}")
        
        print()
    
    # Calculate processing time
    end_time = datetime.now()
    processing_time = end_time - start_time
    
    print("=" * 50)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 50)
    
    if all_results:
        # Export combined results
        combined_filename = f"thrush_audio_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        ml.export_to_csv(all_results, combined_filename)
        
        # Generate summary statistics
        summary = ml.get_species_summary(all_results)
        
        print(f"Processing time: {processing_time}")
        print(f"Total results: {len(all_results)}")
        print(f"Unique species: {summary.get('unique_species', 0)}")
        print(f"Combined results saved to: {combined_filename}")
        
        # Breakdown by region
        print("\nResults by region:")
        region_counts = {}
        for result in all_results:
            region = result.get('region_name', 'Unknown')
            region_counts[region] = region_counts.get(region, 0) + 1
        
        for region, count in sorted(region_counts.items()):
            print(f"  {region}: {count} results")
        
        # Breakdown by species
        print("\nResults by species:")
        species_counts = {}
        for result in all_results:
            species = result.get('common_name', 'Unknown')
            species_counts[species] = species_counts.get(species, 0) + 1
        
        for species, count in sorted(species_counts.items()):
            print(f"  {species}: {count} results")
        
        # Quality analysis (if available)
        if any('quality' in result for result in all_results):
            print("\nQuality distribution:")
            quality_counts = {}
            for result in all_results:
                quality = result.get('quality', 'Unknown')
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
            
            for quality, count in sorted(quality_counts.items()):
                print(f"  Quality {quality}: {count} results")
        
        # Average results per search
        avg_per_search = len(all_results) / total_searches
        print(f"\nAverage results per search: {avg_per_search:.2f}")
        
    else:
        print("No results found across all searches.")
        print("This might indicate:")
        print("  - Network connectivity issues")
        print("  - Invalid search parameters")
        print("  - No matching media in the specified regions/time periods")
    
    print("\nBatch processing tips:")
    print("  - Use appropriate rate limiting to avoid overwhelming servers")
    print("  - Save intermediate results in case of interruption")
    print("  - Consider running during off-peak hours for large batches")
    print("  - Monitor for changes in website structure that might affect parsing")


def demo_advanced_filtering():
    """Demonstrate advanced filtering options."""
    
    print("\n" + "=" * 50)
    print("ADVANCED FILTERING DEMO")
    print("=" * 50)
    
    ml = MacaulayLookup(rate_limit=1.0)
    
    # High-quality recordings only
    print("\n1. High-quality Wood Thrush recordings (A quality, no background)...")
    results = ml.search_species(
        common_name="Wood Thrush",
        region="US-NY",
        begin_month=5,
        end_month=6,
        media_type="audio",
        tag="song",
        quality="A",
        background="0",
        max_results=5
    )
    
    print(f"Found {len(results)} high-quality results")
    
    # Specific recordist
    print("\n2. Recordings by specific quality criteria...")
    results = ml.search_species(
        common_name="American Robin",
        region="US-CA",
        media_type="audio",
        quality="A",
        max_results=3
    )
    
    print(f"Found {len(results)} results with A quality rating")
    
    print("\nAdvanced filtering allows for:")
    print("  - Quality-based selection (A, B, C, D, E ratings)")
    print("  - Background noise filtering (0-4 scale)")
    print("  - Recordist-specific searches")
    print("  - Tag-based filtering (song, call, flight call, etc.)")


if __name__ == "__main__":
    main()
    demo_advanced_filtering()