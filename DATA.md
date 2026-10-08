# Data documentation

## Exact reproduction dataset

The paper-faithful numerical experiment uses the route-specific processed dataset included in this repository at `data/final_data_sbrf_sbgr.csv`.

- Rows: **14,956**
- Columns: **28**
- Route: **SBRF (Recife) to SBGR (São Paulo/Guarulhos)**
- Destination: SBGR
- Study period represented by the parent processed dataset: **2022-2024**
- Extraction rule from the archived processed modeling table: `sg_icao_origem == 2`

The route dataset is an unchanged row/column slice of the archived `final_data_sbgr.csv` used by the executable experiment. The route code column is intentionally retained so that the original source-code route filter remains valid.

The full archived processed table contains 254,183 rows. It is not required by the model after the SBRF-SBGR route selection. The repository also includes a small schema sample and `scripts/prepare_route_dataset.py`; users with the archived parent table can independently regenerate and integrity-check the exact route file.

### Integrity check

For the exact route CSV included in the repository:

```text
SHA-256:
02990049e1307b352b369c0074719ce89d21fbc6aa6156bcd0dd32059819a0eb
```

This checksum is the canonical integrity check for the paper-faithful processed dataset.

## Source data

As described in the paper, the processed table combines:

1. **Active Regular Flight (VRA) Reports** from Brazil's National Civil Aviation Agency (ANAC), providing operational flight information.
2. **METAR observations** for SBGR obtained through the Iowa Environmental Mesonet, providing meteorological variables.

Flights and meteorological observations are merged using the feature-engineering procedure described in the article. The processed modeling table contains encoded/engineered features rather than the raw source records.

## Columns

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

Categorical operational fields are label encoded. Cyclical temporal variables are already represented as sine/cosine pairs.

## Wind-speed clarification

The published methodology table lists sustained wind speed as a conceptual feature. The archived processed table used by the executable final experiment contains **no sustained-wind-speed field**. It contains wind direction (`drct`) and gust speed (`gust_speed`).

Accordingly, after the source-code route filter and removal of non-input/alternate-output columns, the numerical experiment uses **23 input features**. The public reproduction intentionally follows that executable experiment.

A later reconstructed dataset containing an `sknt` field was created during a post-publication diagnostic exercise. It is **not** part of the paper-faithful dataset because it is not the dataset underlying the published numerical results.

## Sample file

`data/sample_sbrf_sbgr.csv` contains the first 20 rows solely for schema inspection. It cannot reproduce the reported paper metrics.

## Regenerating the exact route slice

With the archived `final_data_sbgr.csv` available locally, run:

```bash
python scripts/prepare_route_dataset.py /path/to/final_data_sbgr.csv
```

The script checks the expected 14,956 x 28 shape, writes `data/final_data_sbrf_sbgr.csv`, and verifies the exact SHA-256 checksum.

## Data terms

The repository's MIT License applies to code and the notebooks. Use of the underlying source data remains subject to the applicable ANAC and Iowa Environmental Mesonet terms and attribution requirements.
