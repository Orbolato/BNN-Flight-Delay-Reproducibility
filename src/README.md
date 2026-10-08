# Source notes

The repository-root `reproduce_exact_paper.py` is the canonical, compact implementation for reproducing the published BNN numerical experiment. It intentionally preserves the RNG-sensitive model-construction order, split/scaling behavior, two-stage KL training, and Monte Carlo evaluation sequence that affect the reported results.

The larger development implementation used to generate additional ANN comparisons, SHAP analyses, diagnostics, and publication figures was substantially broader than the numerical reproduction itself. It is not required to reproduce the reported BNN metrics, so the public package keeps the executable path focused and auditable rather than duplicating that analysis script here.

The exact route-specific processed dataset is distributed in `data/final_data_sbrf_sbgr.csv.gz`. `scripts/prepare_route_dataset.py` documents and verifies how that slice is extracted from the archived parent `final_data_sbgr.csv` table.
