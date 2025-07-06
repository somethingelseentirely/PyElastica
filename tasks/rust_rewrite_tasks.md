# Rust Rewrite Tasks

Below is a high-level checklist for incrementally migrating PyElastica's core to Rust with PyO3 bindings. Each bullet can become a separate issue or development milestone.

- [x] **Set up build system** — create a `cargo` workspace, add [maturin](https://github.com/PyO3/maturin) for building, and configure PyO3.
- [ ] **Port contact utilities** — rewrite functions from `contact_utils.py` in Rust.
- [ ] **Move boundary conditions** — translate kernels from `boundary_conditions.py`.
- [ ] **Implement rod update steps** — provide Rust equivalents for time-stepping routines.
- [ ] **Wire into Python** — replace Numba-decorated functions with calls to the Rust extension.
- [ ] **CI integration** — build and test the Rust extension using GitHub Actions.
- [ ] **Update docs and examples** — document the new build process and usage.

