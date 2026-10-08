# BNN Flight Delay Reproducibility

Reproducibility package for:

**Lucas Orbolato Carvalho, Mayara Condé Rocha Murça, Marcelo Xavier Guterres, and Igor Galhano Gomes, “Predicting Arrival Delays and Flight Time Deviations Under Uncertainty Using Bayesian Neural Networks,” IEEE Access, 2026.**  
DOI: https://doi.org/10.1109/ACCESS.2026.3709713

This repository packages the paper-faithful executable experiment, the exact route-specific processed dataset, public reproduction notebooks, and data documentation.

## Repository contents

- `data/final_data_sbrf_sbgr.csv` — exact 14,956-row SBRF-SBGR processed dataset used for the paper-faithful numerical experiment.
- `data/sample_sbrf_sbgr.csv` — 20-row sample for quick schema inspection only.
- `notebooks/paper_reproduction.ipynb` — public notebook for reproducing the published experiment.
- `notebooks/verified_reference_run.ipynb` — preserved verified reference run.
- `reproduce_exact_paper.py` — standalone implementation preserving the numerical details needed for stochastic reproduction.
- `scripts/prepare_route_dataset.py` — extracts the exact route subset from the archived parent `final_data_sbgr.csv` table and verifies its SHA-256 checksum.
- `src/README.md` — notes on the scope of the public source package and the larger development workflow.
- `DATA.md` — data provenance, schema, exact dataset checksum, and the wind-speed reproducibility note.
- `CITATION.cff` — citation metadata for GitHub's “Cite this repository” interface.

## Verified reference result

For the **Arrival Delay coverage-selected BNN**, using seed 42 and the original model-construction/RNG order, the verified reproduction obtained:

| Metric | Reproduction | Paper |
| --- | ---: | ---: |
| Scaled test MSE | 0.00726982 | 0.00727 |
| Test MAE | 6.676 min | 6.68 min |
| 95% coverage | 97.33% | 97.3% |
| Mean posterior prediction SD | 9.972 min | 9.97 min |

The executable benchmark values encoded for the four final BNN configurations are:

| Target | Selection | MAE | 95% coverage |
| --- | --- | ---: | ---: |
| Arrival delay | Loss | 6.45 min | 36.0% |
| Arrival delay | Coverage | 6.68 min | 97.3% |
| Flight-time deviation | Loss | 6.31 min | 32.2% |
| Flight-time deviation | Coverage | 6.44 min | 94.7% |

## Important reproducibility note: sustained wind speed

The paper lists **Wind Speed** among the conceptual input features. However, the archived processed modeling table used by the final executable experiment does not contain a sustained-wind-speed column. After the SBRF-SBGR route filter and source-code column drops, the executable experiment uses **23 input features**, including wind direction (`drct`) and gust speed (`gust_speed`), but not sustained wind speed.

The public notebook and script follow the **executable published experiment**. This distinction is documented explicitly because it can otherwise cause an independent reproduction to diverge from the reported numerical results.

## Quick start

Create an environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The exact processed dataset is already included at:

```text
data/final_data_sbrf_sbgr.csv
```

Run:

```bash
python reproduce_exact_paper.py
```

The standalone script starts with the Arrival Delay coverage-selected configuration. The other three paper configurations are listed in the `RUNS` block and can be enabled there.

You can also open `notebooks/paper_reproduction.ipynb`.

The route-specific dataset intentionally retains `sg_icao_origem`, so the original route-filter statement remains valid and idempotent.

## Dataset integrity and regeneration

The exact route CSV contains **14,956 rows and 28 columns**. Its SHA-256 is:

```text
02990049e1307b352b369c0074719ce89d21fbc6aa6156bcd0dd32059819a0eb
```

If you have the archived parent `final_data_sbgr.csv`, regenerate and verify the route dataset with:

```bash
python scripts/prepare_route_dataset.py /path/to/final_data_sbgr.csv
```

The script writes `data/final_data_sbrf_sbgr.csv`, checks the expected 14,956 x 28 shape, and verifies the exact SHA-256 above. See `DATA.md` for details.

## Data provenance

The processed features were derived from the public data sources described in the paper: Brazilian **ANAC Active Regular Flight (VRA) Reports** and **METAR** observations obtained through the Iowa Environmental Mesonet. The study period is 2022-2024, with São Paulo/Guarulhos (SBGR) as destination. See [`DATA.md`](DATA.md) for details.

Model training is performed after filtering the 254,183-row archived processed SBGR table to SBRF-SBGR. The exact route slice preserves the original row order and columns.

## Reproducibility scope

The implementation deliberately preserves details that materially affect the stochastic result, including:

- pre-shuffling before the train/validation/test split;
- seed 42;
- MinMax scaling behavior;
- two-stage BNN training and KL weighting;
- the original **BNN-then-ANN model-construction order**, which advances PyTorch's RNG state;
- the Monte Carlo evaluation sequence used by the archived executable experiment.

## Citation

If you use this repository, please cite:

> Carvalho, L. O., Murça, M. C. R., Guterres, M. X., & Gomes, I. G. (2026). Predicting Arrival Delays and Flight Time Deviations Under Uncertainty Using Bayesian Neural Networks. *IEEE Access*. https://doi.org/10.1109/ACCESS.2026.3709713

GitHub also exposes the preferred citation through `CITATION.cff`.

## License and data terms

The repository **code and notebooks** are released under the MIT License. The processed dataset is provided for research reproducibility; the MIT License does not override the terms, attribution requirements, or rights associated with the underlying ANAC VRA and Iowa Environmental Mesonet source data. See `DATA.md`.

## Contact

For questions about the paper or reproducibility package, please use the repository's Issues page or the author profile at https://orbolato.github.io/.
