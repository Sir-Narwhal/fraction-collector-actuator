# Fraction Collector Actuator

Automation service that drives a physical fraction collector during a
continuous-chromatography (BioSMB) run. It watches process state in Redis,
switches a diverter valve and advances the fraction collector over Modbus TCP,
and logs fraction metadata (plate, well, timing) to MongoDB.

> **This controls real lab hardware.** Running it against a live process
> connection will move a physical valve and actuator. Do not point it at a
> production Redis/Modbus endpoint unless you mean to.

## How it works

- **Redis** carries live process state from the BioSMB skid (current step,
  flow rates, percent complete) and a set of boolean "intent" flags
  (`discrete-fractionate`, `continuous-fractionate`) that other tooling can
  set to request a collection run.
- **`main.py`** is the service entrypoint. It runs two concurrent loops:
  - `recipes/discrete_collection.py` — collects a single fraction once
    triggered, then clears the trigger flag.
  - `recipes/continuous_collection.py` — repeatedly collects fractions for as
    long as `continuous-fractionate` stays set.
- **`collectionlogic/collector.py`** (`CollectionLogic`) implements the
  actual timing: it waits out the tubing dead-volume (via
  `collectionlogic/deadvolume.py`, computed from the physical tubing lengths
  and diameters in the flow path) before switching the diverter valve, then
  waits out sample volume before switching back. Each fraction's timing and
  well position is written to MongoDB.
- **`fractioncollector/`** models the physical plate/well layout (multiple
  96-well plates, boustrophedon well ordering) and hands out a unique ID per
  well for correlating with MongoDB records.
- **`utils/fraction_collector_com.py`** talks to the PLC over Modbus TCP to
  advance the collector and toggle the diverter valve.

`fraction_driver.py` and `test.py` are standalone scripts kept for manual
exercising of the logic against a live Redis instance; they aren't imported
by the service and aren't part of the automated flow.

## Configuration

All connection details are read from environment variables — nothing
sensitive is hardcoded in the source. Copy [`.env.example`](.env.example) to
`.env` and fill in real values for your environment:

| Variable     | Purpose                                                        |
|--------------|------------------------------------------------------------------|
| `REDIS_URL`  | Host/IP of the Redis instance sharing state with the BioSMB skid |
| `MONGO_URL`  | Full MongoDB connection string (including credentials)           |
| `MODBUS_URL` | Host/IP of the Modbus TCP PLC driving the valve/actuator          |

`.env` is gitignored and excluded from the Docker build context — it must be
present on whatever machine actually runs the service (locally via
`python-dotenv`, or via Docker Compose's `env_file`).

## Running locally

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in real values
python main.py
```

## Running with Docker

```bash
docker compose up --build
```

`compose.yaml` loads configuration from `.env` via `env_file` — make sure
that file exists next to `compose.yaml` on the deployment host.

`buildimage.bat` builds the image and saves it as a tarball under `images/`
for transfer to hosts without registry access.

## Branches, versioning, and releases

- **`main`** is the stable branch — what's actually deployed.
- **`develop`** is where ongoing work lands. Releases are cut from here.

Versioning follows [Semantic Versioning](https://semver.org/) and is fully
automated by [release-please](https://github.com/googleapis/release-please)
based on [Conventional Commits](https://www.conventionalcommits.org/). Write
commit messages like:

- `fix: ...` → patch release (1.0.0 → 1.0.1)
- `feat: ...` → minor release (1.0.0 → 1.1.0)
- `feat!: ...` or a `BREAKING CHANGE:` footer → major release (1.0.0 → 2.0.0)

Every push to `develop` updates a standing "release PR" that accumulates the
changelog and next version number. Merging that PR tags the release, creates
a GitHub Release, and triggers a workflow that builds the Docker image,
saves it as a tarball (same as `buildimage.bat`), and attaches it to the
release as a downloadable asset. Non-conventional commit messages are
rejected by CI on pull requests.
