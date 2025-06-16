#!/usr/bin/env python3
"""
Advanced eBird API Example: Cajas National Park Species List and Media

This example demonstrates how to:
1. Query eBird API for species at a specific hotspot (Cajas National Park)
2. Get media for those species using the Macaulay Library API
3. Save results to CSV with location and date information

Usage:
    python advanced_ebird_example.py
"""

import os
import csv
from typing import List, Dict
from macaulay_library_lookup.ebird_api import eBirdAPI
from macaulay_library_lookup.core import MacaulayLookup
from macaulay_library_lookup.taxonomy import eBirdTaxonomy

def get_species_list_from_hotspot(hotspot_id: str) -> List[Dict]:
    """Get species list from eBird hotspot."""
    api = eBirdAPI(api_key=os.getenv('EBIRD_API_KEY'))
    
    # Get recent observations from the hotspot
    observations = api.get_recent_observations_by_hotspot(
        hotspot_id=hotspot_id,
        days_back=30,  # Get last year of observations
        max_results=500  # Get up to 500 species
    )
    
    # Extract unique species with their observation details
    species_obs = {}
    for obs in observations:
        if 'speciesCode' in obs:
            species_code = obs['speciesCode']
            if species_code not in species_obs:
                species_obs[species_code] = {
                    'species_code': species_code,
                    'common_name': obs.get('comName', ''),
                    'scientific_name': obs.get('sciName', ''),
                    'location': obs.get('locName', ''),
                    'date': obs.get('obsDt', ''),
                    'latitude': obs.get('lat', ''),
                    'longitude': obs.get('lng', '')
                }
    
    return list(species_obs.values())

def get_media_for_species(species_list: List[Dict], output_file: str):
    """Get media for species and save to CSV."""
    # Initialize taxonomy with local file
    taxonomy = eBirdTaxonomy()
    lookup = MacaulayLookup()
    
    # Prepare CSV headers
    headers = ['species_code', 'common_name', 'scientific_name', 
              'location', 'date', 'latitude', 'longitude',
              'catalog_id', 'media_urls']
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        # Process each species
        for species in species_list:
            try:
                # Get media for species
                results = lookup.search_species(species['species_code'])
                
                if results:
                    # Extract media URLs and catalog IDs
                    media_info = []
                    for result in results:
                        if 'media_url' in result and 'catalog_id' in result:
                            media_info.append({
                                'catalog_id': result['catalog_id'],
                                'media_url': result['media_url']
                            })
                    
                    # Write to CSV
                    writer.writerow({
                        'species_code': species['species_code'],
                        'common_name': species['common_name'],
                        'scientific_name': species['scientific_name'],
                        'location': species['location'],
                        'date': species['date'],
                        'latitude': species['latitude'],
                        'longitude': species['longitude'],
                        'catalog_id': ';'.join(info['catalog_id'] for info in media_info),
                        'media_urls': ';'.join(info['media_url'] for info in media_info)
                    })
                    
                    print(f"Processed {species['species_code']}: Found {len(media_info)} media items")
                else:
                    # Write species info even if no media found
                    writer.writerow({
                        'species_code': species['species_code'],
                        'common_name': species['common_name'],
                        'scientific_name': species['scientific_name'],
                        'location': species['location'],
                        'date': species['date'],
                        'latitude': species['latitude'],
                        'longitude': species['longitude'],
                        'catalog_id': '',
                        'media_urls': ''
                    })
                    print(f"No media found for {species['species_code']}")
                    
            except Exception as e:
                print(f"Error processing {species['species_code']}: {e}")

def main():
    # Cajas National Park hotspot ID
    hotspot_id = 'L1890605'
    output_file = 'cajas_species_media.csv'
    
    print(f"Getting species list from hotspot {hotspot_id}...")
    species_list = get_species_list_from_hotspot(hotspot_id)
    print(f"Found {len(species_list)} unique species")
    
    print(f"\nGetting media for species and saving to {output_file}...")
    get_media_for_species(species_list, output_file)
    print("\nDone!")

if __name__ == '__main__':
    main() 