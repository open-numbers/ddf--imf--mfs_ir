# IMF Monetary and Financial Statistics (MFS), Interest Rate Dataset

This DDF dataset contains interest rate data from the IMF's Monetary and Financial Statistics (MFS) database.

To get started with DDF and learn how to use the dataset, please read the
[introduction to DDF][1] and [DDFcsv format document][2].

[1]: https://open-numbers.github.io/ddf.html
[2]: https://docs.google.com/document/d/1aynARjsrSgOKsO1dEqboTqANRD1O9u7J_xmxy8m5jW8

## Indicators

| Indicator ID | Name |
|--------------|------|
| disr_rt_pt_a_pt | Discount Rate, Percent per annum |

## Unit of measurement

Percent per annum

## Data sources

Data is sourced from the IMF's SDMX API:
- Dataset: MFS_IR (Monetary and Financial Statistics - Interest Rates)
- API endpoint: https://api.imf.org/external/sdmx/2.1/

## ETL

See [etl/README.md](etl/README.md) for instructions on updating the dataset.
