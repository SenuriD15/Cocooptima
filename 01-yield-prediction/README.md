# CocoOptima – Component 1: Batch Yield Prediction – Dataset

Daily factory batch records, **2016-01-01 → 2025-12-31**: **20,765 batches**, 8,079 raw-nut lots, and 3 products routed to 4 model groups (SRS YLD-FR-06).

| Model group | Batches | Target (saleable yield %) | Feed definition |
|---|---|---|---|
| Desiccated Coconut (Fine / Medium / Extra Fine / Chips) | 9,012 | median ~47.4 % | pared white kernel |
| Coconut Milk 17 %, 20 % and Coconut Cream 24 % | 6,318 | ~149 % / ~124 % / ~98 % | separated white kernel |
| VCO – Cold Press | 4,567 | median ~47.4 % | dried kernel |
| VCO – Wet Centrifuge (from Oct 2021) | 868 | median ~20.4 % | fresh white kernel |

Target (SRS §5.4): `saleable_yield_pct = accepted_output_kg / product_specific_feed_kg × 100`. Coconut milk can exceed 100 % because extraction water becomes part of the product.

## Layout (SRS §10.3)
```
research/        RESEARCH_REPORT.md, sources/ (real CBSL, weather and events series), scripts/
data_generation/ config.py, generate_dataset.py, build_processed.py, make_data_dictionary.py, validate_dataset.py
data/raw/        factory-system tables: production_batches, raw_material_lots, preprocessing_records,
                 process_checkpoints, qc_final_results (contain normal data-entry issues)
data/interim/    joined + validated table, cleaning_log.txt
data/processed/  yield_desiccated_coconut.csv, yield_coconut_milk.csv, yield_virgin_coconut_oil.csv, yield_all_products.csv
data/splits/     split_definition.json, {train,validation,test}_batch_ids.csv, yield_thresholds_v1.json
data/data_dictionary/data_dictionary.csv   86 fields: unit, description, origin, prediction-time availability
data/VALIDATION_REPORT.md
```

## Splits (chronological, whole batches – SRS §5.6)
train 2016–2022 · validation 2023–2024 · test 2025.

Thresholds and batch-size categories are fitted on train only. The `hist_yield_*` features use only strictly earlier production dates.

## Leakage rules
Use only fields marked `allowed_as_predictor = yes` in the data dictionary for the initial prediction. `checkpoint` fields are for the optional in-process update model (YLD-FR-12) and exist from March 2018 onward. `outcome` fields are never predictors.

## Rebuild
```
cd data_generation
python generate_dataset.py && python build_processed.py && python make_data_dictionary.py && python validate_dataset.py
```
The build is deterministic (seed in `config.py`). Re-running reproduces identical files.

## Construction method
Every value is driven by real Sri Lankan records:
- weather of the sourcing districts (with lags)
- national nut supply and nut price
- curfews, COVID closures, the 2022 power/fuel crisis, floods and Cyclone Ditwah
- public holidays

Batch outcomes come from product mass balances whose parameters are calibrated to published process data (see `research/RESEARCH_REPORT.md`). When real Metshu batch records become available, load them into `data/raw/` with the same schema and rerun `build_processed.py`. The model pipeline does not need to change.
