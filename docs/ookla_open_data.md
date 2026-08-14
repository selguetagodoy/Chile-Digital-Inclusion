# Ookla Open Data layer

This repository uses Speedtest by Ookla Global Fixed and Mobile Network Performance Map Tiles as a separate observed-network-performance layer.

## Current processing

The quarterly builder reads the official global Parquet files from the public `ookla-open-data` AWS S3 bucket, filters a Chile bounding box, and then retains tiles whose centroids fall within the Natural Earth 1:10m Chile ADM0 boundary.

National performance indicators are calculated from the published tile averages weighted by each tile's test count. Fixed and mobile networks remain separate. The repository also retains the Chile-filtered tile records so that regional or commune aggregations can be reproduced later.

`devices_sum_across_tiles` is the sum of the published tile-level device counts and must not be interpreted as a nationally deduplicated device count.

## Source

Official project repository:
https://github.com/teamookla/ookla-open-data

Official data bucket pattern:
https://ookla-open-data.s3.amazonaws.com/parquet/performance/type={fixed|mobile}/year=YYYY/quarter=Q/

## License and attribution

The Ookla Open Data source is distributed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0). Derived Ookla data in `data/ookla/` is therefore not covered by the repository's code license and remains subject to the source terms.

Suggested attribution adapted from the source project:

Speedtest® by Ookla® Global Fixed and Mobile Network Performance Maps, accessed in August 2026 from AWS. Based on Sebastián Elgueta Godoy's analysis of Speedtest® by Ookla® Global Fixed and Mobile Network Performance Maps for the indicated quarterly period. Ookla trademarks used under license and reprinted with permission.

## Interpretation

Ookla measures observed network performance where tests occur. It does not measure universal household access and should not replace Censo, CASEN or SUBTEL indicators of access, devices or digital inclusion.

Last reviewed: 2026-08-13.
