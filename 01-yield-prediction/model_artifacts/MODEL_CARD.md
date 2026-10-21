# Component 1 – Batch Yield models (model card)

Intended use: decision support for production/quality officers before a batch is processed. Not for automatic decisions.

| Model group | Selected model | Test MAE | Test R² | Hist-avg MAE | MLR MAE | 90 % interval ± |
|---|---|---|---|---|---|---|
| Desiccated Coconut | Support vector regression | 0.406 | 0.731 | 0.959 | 0.455 | 0.74 |
| Coconut Milk | Weighted ensemble (Ridge regression 0.73, Hist gradient boosting 0.18, Support vector regression 0.09) | 2.998 | 0.950 | 6.136 | 3.115 | 5.12 |
| VCO - Cold Press | Weighted ensemble (Ridge regression 0.61, Support vector regression 0.18, Hist gradient boosting 0.21) | 0.661 | 0.845 | 1.674 | 0.668 | 1.39 |
| VCO - Wet Centrifuge | Weighted ensemble (Ridge regression 0.54, Random forest 0.36, Hist gradient boosting 0.10) | 0.393 | 0.779 | 0.863 | 0.400 | 0.84 |

Limitations: trained on 2016–2025 batch records of one factory; predictions outside the input ranges in feature_schema.json raise warnings; whole-batch microbiological rejections are not predicted (handled by QC).

Files per group: model_pipeline.joblib, feature_schema.json, metadata.json, metrics.json. Shared: c1_features.py, yield_thresholds_v1.json.