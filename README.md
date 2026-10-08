# BNN Flight Delay Reproducibility

Reproducibility package for:

**Lucas Orbolato Carvalho, Mayara Condé Rocha Murça, Marcelo Xavier Guterres, and Igor Galhano Gomes, “Predicting Arrival Delays and Flight Time Deviations Under Uncertainty Using Bayesian Neural Networks,” IEEE Access, 2026.**  
DOI: https://doi.org/10.1109/ACCESS.2026.3709713

This repository packages the executable experiment used for the paper together with a compact, route-specific processed dataset and notebooks that reproduce the reported Bayesian neural network (BNN) results.

## Repository contents

- `notebooks/paper_reproduction.ipynb` — cleaned notebook reproducing the published experiment.
- `notebooks/verified_reference_run.ipynb` — executed reference notebook documenting a verified reproduction run.
- `reproduce_exact_paper.py` — standalone reproduction script.
- `src/delay_pred_enhanced.py` — archived experiment implementation, with only the dataset path made portable.
- `data/final_data_sbrf_sbgr.csv.gz` — exact 14,956-row SBRF-SBGR processed subset used after the route filter in the published experiment.
- `data/sample_sbrf_sbgr.csv` — 100-row sample for inspection/smoke testing only.
- `DATA.md` — data provenance, schema, and the wind-speed reproducibility note.
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

The paper lists **Wind Speed** among the conceptual input features. However, the archived processed modeling table used by the final executable experiment does not contain a sustained-wind-speed column. After the SBRF-SBGR route filter and the source-code column drops, the executable experiment uses **23 input features**, including wind direction (`drct`) and gust speed (`gust_speed`), but not sustained wind speed.

The notebooks in this repository follow the **executable published experiment**. This distinction is documented explicitly because it can otherwise cause a well-implemented independent reproduction to diverge from the reported numerical results.

## Quick start

Create a Python environment and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then run:

```bash
python reproduce_exact_paper.py
```

The standalone script starts with the Arrival Delay coverage-selected configuration. The other three paper configurations are listed in the `RUNS` block and can be enabled there.

You can also open:

```text
notebooks/paper_reproduction.ipynb
```

The route-specific dataset intentionally retains `sg_icao_origem`, so the original route-filter statement remains valid and idempotent.

## Data provenance

The processed features were derived from the public data sources described in the paper: Brazilian **ANAC Active Regular Flight (VRA) Reports** and **METAR** observations obtained through the Iowa Environmental Mesonet. The study period is 2022-2024, with São Paulo/Guarulhos (SBGR) as destination. See [`DATA.md`](DATA.md) for additional details.

The repository distributes the route-specific processed modeling subset rather than the full 254,183-row intermediate table because model training is performed after filtering to SBRF-SBGR. The subset preserves the row order and columns of that exact slice.

## Reproducibility scope

This repository is intended to reproduce the numerical modeling experiment, including implementation details that materially affect stochastic reproduction, such as:

- pre-shuffling before the train/validation/test split;
- seed 42;
- MinMax scaling behavior;
- two-stage BNN training and KL weighting;
- the original BNN/ANN model-construction order, which advances PyTorch's RNG state;
- the Monte Carlo evaluation sequence used by the source implementation.

The archived `src/delay_pred_enhanced.py` contains the broader analysis/plotting implementation. `reproduce_exact_paper.py` and the notebooks isolate the core logic required to reproduce the reported BNN results.

## Citation

If you use this repository, please cite the associated article:

> Carvalho, L. O., Murça, M. C. R., Guterres, M. X., & Gomes, I. G. (2026). Predicting Arrival Delays and Flight Time Deviations Under Uncertainty Using Bayesian Neural Networks. *IEEE Access*. https://doi.org/10.1109/ACCESS.2026.3709713

GitHub also exposes the citation through `CITATION.cff`.

## License and data terms

The repository **code and notebooks** are released under the MIT License. The processed dataset is provided for research reproducibility; the MIT License does not override the terms, attribution requirements, or rights associated with the underlying ANAC VRA and Iowa Environmental Mesonet source data. See `DATA.md`.

## Contact

For questions about the paper or reproducibility package, please use the repository's Issues page or the author profile at https://orbolato.github.io/.
