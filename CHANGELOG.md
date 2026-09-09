# Changelog

## 1.0.0 (2026-09-09)

### Features

* Externalize Redis/MongoDB/Modbus configuration into environment variables (`.env`) instead of hardcoding credentials and internal IPs in source
* Add README documenting architecture, configuration, and how to run locally/via Docker
* Add MIT license
* Add `.gitignore` / `.dockerignore` hygiene so secrets and build artifacts never get committed or baked into the image
* Add automated release pipeline (release-please, conventional commits) starting at this version

### Bug Fixes

* Fix `NameError` in Modbus client cleanup (`utils/fraction_collector_com.py`) when the connection itself failed to open
* Fix invalid `Dict[str:float, str:str]` type hints
* Fix Python 3.12-only f-string syntax in `recipes/discrete_collection.py`
* Fix `MONGO_URL` override in `main.py` that was read but never actually passed through to `CollectionLogic`
