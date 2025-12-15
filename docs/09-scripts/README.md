# Scripts & CLI Tools

This project has two “human friendly” ways to run research from the repository:

- `run_research.py` (repo root): stable entrypoint used by docs
- `scripts/research/cli.py`: same CLI, useful if you’re working inside `scripts/`

There’s also a minimal demo script:

- `examples/hello_research.py`: simple “hello world” prototype

---

## Main CLI (recommended)

### Help / usage

```bash
python run_research.py --help
```

### Single-company research

```bash
python run_research.py --company "Microsoft"
python run_research.py --company "Tesla" --depth comprehensive
```

### YAML profile research

```bash
python run_research.py --profile research_targets/company.yaml
```

### Market folder research (all `*.yaml` profiles in a directory)

```bash
python run_research.py --market research_targets/paraguay_telecom/
```

### Switch execution engine

```bash
# Default: orchestration engine (recommended)
python run_research.py --company "Apple"

# Direct LangGraph run (useful for debugging)
python run_research.py --company "Apple" --use-graph
```

### Output location

```bash
python run_research.py --company "Stripe" --output outputs/research
```

---

## CLI options (current)

The CLI supports these top-level options:

- **Input**: `--company`, `--profile`, `--market` (one is required)
- **Research**: `--depth` (`quick|standard|comprehensive`), `--use-graph`, `--output`, `--compare`
- **Utility**: `--show-config`, `--dry-run`, `--verbose`

---

## Output structure

Per company:

```
outputs/research/<company_slug>/
├── 00_full_report.md
├── metrics.json
└── extracted_data.json   (when available)
```

---

## YAML input formats

### Company profile (minimal)

```yaml
name: Tigo Paraguay
```

Additional keys are allowed; the CLI currently requires only `name`.

---

## Specialized research scripts

The `scripts/research/` folder contains one-off runners (e.g. Paraguay telecom variants) that are useful as references, but they may have hardcoded paths or assumptions. Prefer the main CLI unless you’re working on that specific workflow.

---

**Related documentation**

- [Quick Start](../01-overview/QUICKSTART.md)
- [Configuration](../06-configuration/README.md)

