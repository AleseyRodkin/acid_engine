# AcidEngine Roadmap

## What is AcidEngine

AcidEngine is a **contract-driven data control layer**. Instead of writing scattered if/else checks, you describe your data rules once in a Contract, and AcidEngine enforces them automatically — whether your data lives in CSV files, Pandas DataFrames, LLM outputs, or APIs.

**Key principles:**
- **Contract is the single source of truth** — all data rules live in one place
- **Enforcement, not validation** — data that violates the contract cannot enter your system
- **Works with your existing stack** — Pandas, Pydantic, Pandera are not replaced, but complemented
- **From validation to pipeline** — the same Contract can generate production-ready Python pipelines

**Open Core Model:** The core is and always will be free under Apache 2.0. Enterprise features (Registry, Audit Trail, SSO, monitoring) will be offered under a commercial license.

---

## Current Status: v1.0 (Stable)

The core is production-ready. Every feature below is implemented, tested, and available on PyPI.

### Data Contracts
Describe rules declaratively — types, ranges, formats, cross-field dependencies — and they are enforced at runtime.

- [x] **Field Contracts** — per-value contracts: type, min/max, regex, choices, custom validators, 8 built-in presets (Email, Url, UUID, etc.)
- [x] **Container Contracts** — collection-level guarantees: uniqueness, ordering, immutability
- [x] **Cross‑Field Validation** — business rules linking fields (e.g., `age >= 18 if email.endswith('@company.com')`), safe evaluation without `eval()`

### Quality Control
Control what happens when data violates the contract — from silent filtering to full rollback.

- [x] **QualityGate** — 4 modes: strict (rollback), recovery (rollback + save good records), audit (rollback + save all), quarantine (filter without rollback)
- [x] **ErrorRecord** — structured error capture with expected/received/reason for every violation
- [x] **Explain Engine** — human-readable reports with statistics, top violations, and sample errors, exportable to Markdown

### Integration and Interoperability
AcidEngine doesn't replace your stack — it strengthens it.

- [x] **Pandas Integration** — validate DataFrames directly via `contract.validate(df)`
- [x] **CSV Loader** — load and validate CSV files with automatic contract generation
- [x] **YAML Support** — import/export contracts as YAML files for version control and sharing
- [x] **Smart Contract Generator** — analyze a data sample and suggest a contract automatically

### AI and LLM Guardrails
Contracts can validate LLM outputs as easily as CSV data.

- [x] **AI Guard** — validate LLM responses (JSON/dict) against a contract
- [x] **LangChain Plugin** — drop-in guard for LangChain pipelines (`AcidOutputGuard`)

### Pipeline Generation
The same Contract that validates data can also generate the code structure for your data pipeline.

- [x] **Pipeline Generator** — generate Python pipeline skeletons with orchestrator and workers from a contract

### Project Health
- [x] **Test Suite** — 15 smoke tests covering all core components
- [x] **CI via GitHub Actions** — automated testing on every push
- [x] **PyPI Package** — `pip install acid-engine`
- [x] **Documentation** — README (EN/RU), ARCHITECTURE.md, demo scripts

---

## Next: v1.1 (Short-term, Open Core)

Smaller improvements that add immediate practical value.

- [ ] **Polars Integration** — same interface as Pandas, for Polars users
- [ ] **Enhanced Explain Engine** — violation history, per-field top violations
- [ ] **JSON Schema export** — generate JSON Schema from a Contract
- [ ] **Extended Field Presets** — Date, DateTime, Boolean out of the box

---

## Planned: v1.5 (Medium-term, Open Core)

Features that deepen the contract-driven approach and strengthen the developer experience.

- [ ] **Full Pipeline Generation** — auto-generate code for standard operations (deduplicate, cast, normalize)
- [ ] **Contract Diff** — compare two versions of a contract and see what changed
- [ ] **Soft Contracts** — INFO / WARNING / ERROR severity levels for gradual adoption
- [ ] **Contract Fingerprint** — hash for compatibility checks between systems

---

## Future: v2.0 (Long-term, Open Core)

Scalability and ecosystem.

- [ ] **Rust Runtime** — high-performance core for heavy workloads
- [ ] **Kafka / Spark Streaming Plugins** — validate data in real-time pipelines
- [ ] **Marketplace of Contracts** — public registry for sharing and discovering contracts

---

## Enterprise Features (Closed Source, Commercial License)

Features designed for large teams and regulated industries. Available under a commercial license.

- [ ] **Contract Registry** — centralized catalog with versioning, dependencies, and role-based access
- [ ] **Audit Trail** — full history of validations, changes, and who made them
- [ ] **SSO and RBAC** — enterprise authentication and role-based access control
- [ ] **Advanced Monitoring** — Prometheus/Grafana dashboards for contract performance
- [ ] **Drift Detection** — monitor how data quality changes over time
- [ ] **Visual Contract Designer** — Web UI for building and managing contracts
- [ ] **SaaS Platform** — managed cloud offering

---

AcidEngine is a living project. Priorities are driven by real user feedback. If you have a use case that's not covered here, open an issue on GitHub or write to the author.
