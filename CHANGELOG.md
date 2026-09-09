# Changelog

## [1.1.0](https://github.com/Sir-Narwhal/fraction-collector-actuator/compare/fraction-collector-actuator-v1.0.0...fraction-collector-actuator-v1.1.0) (2026-09-09)


### Features

* externalize secrets, add docs, and bootstrap release automation ([be2f429](https://github.com/Sir-Narwhal/fraction-collector-actuator/commit/be2f42984bc6d29116910f19dc2228a77bc0b9ed))


### Bug Fixes

* repair commitlint CI job ([e2e439a](https://github.com/Sir-Narwhal/fraction-collector-actuator/commit/e2e439a3ec222d57ab5f96a56d73dc8a9bfe0e07))

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
