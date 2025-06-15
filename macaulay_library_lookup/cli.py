"""Command line interface for MacaulayLibraryLookup."""

import csv
import os
import sys
from typing import List, Optional

import click
import pandas as pd

from .core import MacaulayLookup


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """MacaulayLibraryLookup - Automate Macaulay Library media searches."""
    pass


@cli.command()
@click.option('--species', help='Species common name (e.g., "American Robin")')
@click.option('--scientific-name', help='Species scientific name')
@click.option('--taxon-code', help='eBird species code')
@click.option('--species-file', type=click.Path(exists=True), 
              help='File with list of species (one per line)')
@click.option('--region', help='Geographic region code (e.g., "US-NY")')
@click.option('--month', type=int, help='Single month (1-12)')
@click.option('--begin-month', type=int, help='Starting month (1-12)')
@click.option('--end-month', type=int, help='Ending month (1-12)')
@click.option('--media-type', default='audio', 
              type=click.Choice(['audio', 'photo', 'video']),
              help='Type of media to search for')
@click.option('--tag', help='Media tag (e.g., "song", "call")')
@click.option('--quality', type=click.Choice(['A', 'B', 'C', 'D', 'E']),
              help='Quality rating')
@click.option('--background', type=click.Choice(['0', '1', '2', '3', '4']),
              help='Background noise level')
@click.option('--recordist', help='Name of recordist')
@click.option('--max-results', default=100, type=int,
              help='Maximum number of results per species')
@click.option('--output', default='macaulay_results.csv',
              help='Output CSV filename')
@click.option('--ebird-api-key', help='eBird API key')
@click.option('--rate-limit', default=1.0, type=float,
              help='Rate limit between requests (seconds)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def search(species, scientific_name, taxon_code, species_file, region, month,
           begin_month, end_month, media_type, tag, quality, background,
           recordist, max_results, output, ebird_api_key, rate_limit, verbose):
    """Search for media in the Macaulay Library."""
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    # Initialize lookup tool
    ml = MacaulayLookup(ebird_api_key=ebird_api_key, rate_limit=rate_limit)
    
    results = []
    
    # Handle different input methods
    if species_file:
        # Read species from file
        species_list = []
        with open(species_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    species_list.append(line)
        
        click.echo(f"Searching for {len(species_list)} species from file...")
        results = ml.search_multiple_species(
            species_list,
            region=region,
            begin_month=begin_month or month,
            end_month=end_month or month,
            media_type=media_type,
            tag=tag,
            max_results_per_species=max_results
        )
    
    elif species or scientific_name or taxon_code:
        # Single species search
        click.echo(f"Searching for single species...")
        results = ml.search_species(
            common_name=species,
            scientific_name=scientific_name,
            taxon_code=taxon_code,
            region=region,
            begin_month=begin_month,
            end_month=end_month,
            month=month,
            media_type=media_type,
            tag=tag,
            quality=quality,
            background=background,
            recordist=recordist,
            max_results=max_results
        )
    
    else:
        click.echo("Error: Must specify either --species, --scientific-name, --taxon-code, or --species-file")
        sys.exit(1)
    
    # Export results
    if results:
        ml.export_to_csv(results, output)
        click.echo(f"Exported {len(results)} records to {output}")
        
        # Show summary
        summary = ml.get_species_summary(results)
        click.echo(f"\nSummary:")
        click.echo(f"  Total records: {summary.get('total_records', 0)}")
        click.echo(f"  Unique species: {summary.get('unique_species', 0)}")
        
        if summary.get('media_types'):
            click.echo(f"  Media types: {dict(summary['media_types'])}")
        
    else:
        click.echo("No results found.")


@cli.command()
@click.option('--hotspot-id', required=True, help='eBird hotspot ID (e.g., "L12345")')
@click.option('--days-back', default=30, type=int, help='Days back to search')
@click.option('--region', help='Geographic region for media search')
@click.option('--begin-month', type=int, help='Starting month for media search')
@click.option('--end-month', type=int, help='Ending month for media search')
@click.option('--media-type', default='audio',
              type=click.Choice(['audio', 'photo', 'video']),
              help='Type of media to search for')
@click.option('--max-results', default=20, type=int,
              help='Maximum results per species')
@click.option('--output', default='hotspot_results.csv',
              help='Output CSV filename')
@click.option('--ebird-api-key', help='eBird API key (required)')
@click.option('--rate-limit', default=1.0, type=float,
              help='Rate limit between requests')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def hotspot(hotspot_id, days_back, region, begin_month, end_month, media_type,
            max_results, output, ebird_api_key, rate_limit, verbose):
    """Search for media based on species from an eBird hotspot."""
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    if not ebird_api_key:
        ebird_api_key = os.getenv('EBIRD_API_KEY')
        if not ebird_api_key:
            click.echo("Error: eBird API key required for hotspot searches")
            click.echo("Set EBIRD_API_KEY environment variable or use --ebird-api-key")
            sys.exit(1)
    
    # Initialize lookup tool
    ml = MacaulayLookup(ebird_api_key=ebird_api_key, rate_limit=rate_limit)
    
    click.echo(f"Searching hotspot {hotspot_id}...")
    
    results = ml.search_from_ebird_hotspot(
        hotspot_id=hotspot_id,
        days_back=days_back,
        region=region,
        begin_month=begin_month,
        end_month=end_month,
        media_type=media_type,
        max_results_per_species=max_results
    )
    
    if results:
        ml.export_to_csv(results, output)
        click.echo(f"Exported {len(results)} records to {output}")
        
        # Show summary
        summary = ml.get_species_summary(results)
        click.echo(f"\nSummary:")
        click.echo(f"  Total records: {summary.get('total_records', 0)}")
        click.echo(f"  Unique species: {summary.get('unique_species', 0)}")
        
    else:
        click.echo("No results found.")


@cli.command()
@click.option('--query', required=True, help='Species search query')
@click.option('--limit', default=10, type=int, help='Maximum number of results')
def species_search(query, limit):
    """Search for species in the eBird taxonomy."""
    
    from .taxonomy import eBirdTaxonomy
    
    taxonomy = eBirdTaxonomy()
    results = taxonomy.search_species(query, limit)
    
    if results:
        click.echo(f"Found {len(results)} matching species:")
        click.echo()
        
        for species in results:
            click.echo(f"  {species['common_name']}")
            click.echo(f"    Scientific: {species['scientific_name']}")
            click.echo(f"    Code: {species['species_code']}")
            click.echo()
    else:
        click.echo(f"No species found matching '{query}'")


@cli.command()
@click.argument('csv_file', type=click.Path(exists=True))
def validate(csv_file):
    """Validate a CSV file with search results."""
    
    try:
        df = pd.read_csv(csv_file)
        
        required_columns = ['catalog_id', 'species_code', 'common_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            click.echo(f"Error: Missing required columns: {missing_columns}")
            sys.exit(1)
        
        # Check for valid catalog IDs
        invalid_ids = df[~df['catalog_id'].astype(str).str.isdigit()]
        if not invalid_ids.empty:
            click.echo(f"Warning: {len(invalid_ids)} records with invalid catalog IDs")
        
        # Summary statistics
        click.echo(f"CSV validation results:")
        click.echo(f"  Total records: {len(df)}")
        click.echo(f"  Unique species: {df['common_name'].nunique()}")
        click.echo(f"  Unique catalog IDs: {df['catalog_id'].nunique()}")
        
        if 'media_type' in df.columns:
            click.echo(f"  Media types: {dict(df['media_type'].value_counts())}")
        
        click.echo("✓ CSV file is valid")
        
    except Exception as e:
        click.echo(f"Error validating CSV: {e}")
        sys.exit(1)


@cli.command()
def examples():
    """Show usage examples."""
    
    examples_text = """
MacaulayLibraryLookup Usage Examples:

1. Search for American Robin audio in New York during May:
   macaulay-lookup search --species "American Robin" --region "US-NY" --month 5 --media-type audio --tag song

2. Search for multiple species from a file:
   macaulay-lookup search --species-file species_list.txt --region "US-CA" --media-type photo

3. Search hotspot for recent species:
   macaulay-lookup hotspot --hotspot-id "L12345" --days-back 7 --media-type audio

4. Search with quality filters:
   macaulay-lookup search --species "Wood Thrush" --quality A --background 0 --region "US-NY"

5. Find species in taxonomy:
   macaulay-lookup species-search --query "Robin"

6. Validate results file:
   macaulay-lookup validate results.csv

For more information, use --help with any command.
    """
    
    click.echo(examples_text)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()