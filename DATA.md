# Data documentation

## Public reproduction dataset

`data/final_data_sbrf_sbgr.csv.gz` is the route-specific processed dataset used by this reproducibility package.

- Rows: **14,956**
- Columns: **28**
- Route: **SBRF (Recife) to SBGR (São Paulo/Guarulhos)**
- Destination: SBGR
- Study period represented by the parent processed dataset: **2022-2024**
- Extraction rule from the archived processed modeling table: `sg_icao_origem == 2`

The file is an unchanged row/column slice of the archived `final_data_sbgr.csv` used by the executable experiment. The route code column is intentionally retained so that the original source-code route filter remains valid.

The full archived processed table contains 254,183 rows. It is not required to reproduce the route-specific models and is therefore not distributed here.

## Source data

As described in the paper, the processed table combines:

1. **Active Regular Flight (VRA) Reports** from Brazil's National Civil Aviation Agency (ANAC), providing operational flight information.
2. **METAR observations** for SBGR obtained through the Iowa Environmental Mesonet, providing meteorological variables.

Flights and meteorological observations are merged using the feature-engineering procedure described in the article. The public file in this repository contains processed/encoded modeling features rather than raw flight records.

## Columns

The distributed table contains:

```text
drct
vsby
ceiling
tmpf
dwpf
relh
alti
gust_speed
ifr
lifr
ts
feel
tmi_duration
rate_nm
arrival_demand
sg_icao_empresa
sg_icao_origem
model_equip
scheduled_flight_time
adjusted_arrival_time_sin
adjusted_arrival_time_cos
adjusted_arrival_day_sin
adjusted_arrival_day_cos
adjusted_arrival_month_sin
adjusted_arrival_month_cos
departure_delay
flight_time_deviation
arrival_delay
```

Categorical operational fields in this processed table are label encoded. Cyclical temporal variables are already represented as sine/cosine pairs.

## Wind-speed clarification

The published methodology table lists sustained wind speed as a conceptual feature. The archived processed table used by the executable final experiment contains **no sustained-wind-speed field**. It contains wind direction (`drct`) and gust speed (`gust_speed`).

Accordingly, after the source-code route filter and removal of non-input/alternate-output columns, the numerical experiment uses **23 input features**. The reproduction notebooks intentionally follow that executable experiment.

A later reconstructed dataset containing an `sknt` field was created during a post-publication diagnostic exercise. It is **not** part of this repository because it is not the dataset underlying the published numerical results.

## Sample file

`data/sample_sbrf_sbgr.csv` contains the first 100 rows solely for schema inspection and smoke testing. It cannot reproduce the reported paper metrics.

## Data terms

The repository's MIT License applies to code and notebooks. The processed dataset is supplied for reproducibility of the published study; use of the underlying source data remains subject to the applicable ANAC and Iowa Environmental Mesonet terms and attribution requirements.
