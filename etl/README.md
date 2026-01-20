# ETL Scripts

## Prerequisites

```bash
cd etl
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Update source data

Fetch latest data from IMF API:

```bash
python scripts/update_source.py
```

## Generate DDF files

Transform source data to DDF format:

```bash
python scripts/etl.py
```

## Validate

Validate the dataset and generate datapackage.json:

```bash
cd ..
validate-ddf-ng -p
```

## Adding more indicators

1. Find available indicators in `source/indicators.json` (72 indicators available)
2. Add indicator codes to the `INDICATORS` list in both `scripts/update_source.py` and `scripts/etl.py`
3. Run the ETL: `python scripts/update_source.py && python scripts/etl.py`
4. Validate: `validate-ddf-ng -p`

## Scripts

- `update_source.py` - Fetch data from IMF SDMX API
- `etl.py` - Transform source data to DDF format
