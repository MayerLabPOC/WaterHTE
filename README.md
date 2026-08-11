# High-Throughput Kinetics Enable Predicting Reactivity Across Mechanisms of Acid/Base Catalysis in Water

Data, scripts, and machine learning models associated with the study:

> **High-Throughput Kinetics Enable Predicting Reactivity Across Mechanisms of Acid/Base Catalysis in Water**
> Stefan Kuffer, Robert J. Mayer

Folder names refer to the corresponding sections of the Supporting Information (SI).

## Repository Structure

| Folder | Contents |
|---|---|
| `section2_nmr/` | NMR raw data (Mnova) for synthesis and product characterization (SI sections 2–3) |
| `section4_hydration/` | Stopped-flow kinetics and analysis of acetaldehyde hydration (SI section 4) |
| `section9_kinetics/` | Kinetic datasets and mechanistic analysis, one subfolder per aldehyde (SI sections 8–9) |
| `section10_ml_regression/` | ML datasets, notebooks, and results, one subfolder per SI subsection 10.3.1–10.3.5 |
| `section13_dft/` | Gaussian 16 output files: optimizations (`fopt/`) and single points (`sp_high/`) (SI section 13) |
| `script_batchkinetics/` | Automated fitting of kinetic traces, with example data (SI section 5.5) |

## Notes

- `section9_kinetics/`: `cX_data.xlsx` contains the quality-filtered measurements (`k_obs = NN` for
  failed experiments); for C3, C4, C12, and C14, `cX_data_unfiltered.xlsx` additionally contains the
  complete set before buffer filtering. In total: 8808 experiments, 7200 rate constants, 6889 after
  quality filtering. Column abbreviations are explained in SI Table S24.
- `section10_ml_regression/`: `dataset_r2filtered_ml.xlsx` holds the 6889 quality-filtered rate
  constants used for all ML analyses.

## Authors

Stefan Kuffer, Robert J. Mayer (robert.j.mayer@tum.de)