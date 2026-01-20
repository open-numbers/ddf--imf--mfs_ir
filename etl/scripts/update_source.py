"""
Fetch data from IMF MFS_IR (Interest Rates) API and save to source folder.

Usage:
    cd etl
    source .venv/bin/activate
    python scripts/update_source.py
"""

import json
from pathlib import Path

import sdmx

# List of indicators to fetch (annual frequency only)
# Add more indicators here as needed
INDICATORS = [
    "DISR_RT_PT_A_PT",  # Discount Rate, Percent per annum
]

# Output directory
SOURCE_DIR = Path(__file__).parent.parent / "source"


def fetch_metadata(client: sdmx.Client) -> dict:
    """Fetch and return metadata (codelists) from the MFS_IR dataflow."""
    print("Fetching MFS_IR metadata...")
    dataflow = client.dataflow("MFS_IR")

    metadata = {}
    for codelist_id, codelist in dataflow.codelist.items():
        codes = {}
        for code in codelist:
            code_id = str(code.id) if hasattr(code, "id") else str(code)
            name = str(code.name) if hasattr(code, "name") and code.name else code_id
            codes[code_id] = name
        metadata[codelist_id] = codes

    return metadata


def fetch_data(client: sdmx.Client, indicator: str) -> dict:
    """Fetch data for a specific indicator (all countries, annual frequency)."""
    print(f"Fetching data for {indicator}...")

    # Key format based on dimensions: COUNTRY.INDICATOR.FREQUENCY
    # Empty first position = all countries, then indicator, then A for annual
    data_msg = client.data("MFS_IR", key=f".{indicator}.A")

    df = sdmx.to_pandas(data_msg)

    if df.empty:
        print(f"  No data found for {indicator}")
        return {}

    # Reset index to get a flat dataframe
    df = df.reset_index()

    # Keep only relevant columns
    df = df[["TIME_PERIOD", "COUNTRY", "value"]]
    df.columns = ["year", "country", "value"]

    # Remove NaN values
    total_before = len(df)
    df = df.dropna(subset=["value"])
    nan_count = total_before - len(df)
    if nan_count > 0:
        print(f"  Dropped {nan_count} rows with NaN values")

    # Convert to records
    records = df.to_dict(orient="records")
    print(f"  Found {len(records)} records")

    return records


def main():
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    print("Connecting to IMF_DATA...")
    client = sdmx.Client("IMF_DATA")

    # Fetch and save metadata
    metadata = fetch_metadata(client)

    with open(SOURCE_DIR / "mfs_ir_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to {SOURCE_DIR / 'mfs_ir_metadata.json'}")

    # Save indicators codelist separately for easy access
    indicators = metadata.get("CL_MFS_IR_INDICATOR", {})
    with open(SOURCE_DIR / "indicators.json", "w") as f:
        json.dump(indicators, f, indent=2)
    print(f"Indicators saved to {SOURCE_DIR / 'indicators.json'}")

    # Save countries codelist
    countries = metadata.get("CL_COUNTRY", {})
    with open(SOURCE_DIR / "countries.json", "w") as f:
        json.dump(countries, f, indent=2)
    print(f"Countries saved to {SOURCE_DIR / 'countries.json'}")

    # Fetch data for each indicator
    for indicator in INDICATORS:
        records = fetch_data(client, indicator)
        if records:
            output_file = SOURCE_DIR / f"{indicator}.json"
            with open(output_file, "w") as f:
                json.dump(records, f, indent=2)
            print(f"Data saved to {output_file}")

    print("\nDone!")


if __name__ == "__main__":
    main()
