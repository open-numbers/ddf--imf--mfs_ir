"""
Transform IMF MFS_IR source data into DDF format.

Usage:
    cd etl
    source .venv/bin/activate
    python scripts/etl.py
"""

import json
from pathlib import Path

import polars as pl

# Paths
SOURCE_DIR = Path(__file__).parent.parent / "source"
OUTPUT_DIR = Path(__file__).parent.parent.parent  # Root of DDF dataset

# List of indicators to process (must match update_source.py)
INDICATORS = [
    "DISR_RT_PT_A_PT",  # Discount Rate, Percent per annum
]


def load_metadata() -> tuple[dict, dict]:
    """Load indicator and country metadata."""
    with open(SOURCE_DIR / "indicators.json") as f:
        indicators = json.load(f)

    with open(SOURCE_DIR / "countries.json") as f:
        countries = json.load(f)

    return indicators, countries


def create_concepts(indicators: dict) -> pl.DataFrame:
    """Create concepts dataframe."""
    # Base concepts
    concepts = [
        {"concept": "name", "concept_type": "string", "name": "Name"},
        {"concept": "country", "concept_type": "entity_domain", "name": "Country"},
        {"concept": "year", "concept_type": "time", "name": "Year"},
    ]

    # Add indicator concepts
    for indicator_id, indicator_name in indicators.items():
        if indicator_id in INDICATORS:
            concept_id = indicator_id.lower()
            concepts.append(
                {
                    "concept": concept_id,
                    "concept_type": "measure",
                    "name": indicator_name,
                }
            )

    return pl.DataFrame(concepts)


def create_entities(countries: dict, data_countries: set) -> pl.DataFrame:
    """Create country entities dataframe.

    Only include countries that have data.
    """
    entities = []
    for country_id, country_name in countries.items():
        if country_id in data_countries:
            entities.append({"country": country_id.lower(), "name": country_name})

    return pl.DataFrame(entities).sort("country")


def create_datapoints(indicator_id: str) -> pl.DataFrame:
    """Create datapoints dataframe for an indicator."""
    source_file = SOURCE_DIR / f"{indicator_id}.json"

    with open(source_file) as f:
        data = json.load(f)

    df = pl.DataFrame(data)

    # Rename and transform columns
    concept_id = indicator_id.lower()
    df = df.rename({"value": concept_id})

    # Drop rows with null/NaN values
    df = df.drop_nulls(concept_id)

    # Lowercase country codes
    df = df.with_columns(pl.col("country").str.to_lowercase())

    # Ensure year is string (it should already be)
    df = df.with_columns(pl.col("year").cast(pl.Utf8))

    # Sort by country and year
    df = df.sort(["country", "year"])

    return df


def main():
    print("Loading metadata...")
    indicators, countries = load_metadata()

    # Get set of countries that have data
    data_countries = set()
    for indicator_id in INDICATORS:
        source_file = SOURCE_DIR / f"{indicator_id}.json"
        with open(source_file) as f:
            data = json.load(f)
        for record in data:
            data_countries.add(record["country"])

    print(f"Found {len(data_countries)} countries with data")

    # Create and save concepts
    print("Creating concepts...")
    concepts_df = create_concepts(indicators)
    concepts_file = OUTPUT_DIR / "ddf--concepts.csv"
    concepts_df.write_csv(concepts_file)
    print(f"Saved {concepts_file}")

    # Create and save entities
    print("Creating country entities...")
    entities_df = create_entities(countries, data_countries)
    entities_file = OUTPUT_DIR / "ddf--entities--country.csv"
    entities_df.write_csv(entities_file)
    print(f"Saved {entities_file} ({len(entities_df)} countries)")

    # Create and save datapoints for each indicator
    for indicator_id in INDICATORS:
        print(f"Creating datapoints for {indicator_id}...")
        datapoints_df = create_datapoints(indicator_id)
        concept_id = indicator_id.lower()
        datapoints_file = (
            OUTPUT_DIR / f"ddf--datapoints--{concept_id}--by--country--year.csv"
        )
        datapoints_df.write_csv(datapoints_file)
        print(f"Saved {datapoints_file} ({len(datapoints_df)} datapoints)")

    print("\nDone!")


if __name__ == "__main__":
    main()
