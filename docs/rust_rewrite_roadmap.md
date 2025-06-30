# Rust Rewrite Roadmap

This roadmap proposes migrating performance‐critical portions of PyElastica to Rust with [PyO3](https://pyo3.rs) bindings. The goal is to preserve the existing Python API while gaining speed and memory safety.

## Context
- The current implementation relies on Python with Numba for acceleration, as shown in the dependencies list:

```
The core of PyElastica is developed using:
- numpy
- numba
- scipy
- tqdm
- matplotlib (visualization)
```

- Earlier documentation mentioned a C++ rewrite "Elastica++" scheduled for 2024 Q4:

```
Elastica++ is a C++ implementation of Elastica. The expected release date for the beta version is 2024 Q4.
```

While the original C++ re-release appears inactive, we can build on the same idea using Rust.

## Incremental plan

1. **Identify critical modules**
   - Profile existing code to locate hot spots (e.g., contact calculations, boundary conditions).
   - Start with modules that are already heavily `@njit` decorated.
2. **Create Rust crate**
   - Initialize a new `elastica_rust` crate using `maturin`.
   - Use [maturin](https://github.com/PyO3/maturin) to build and package the Python extension.
   - Configure PyO3 to expose Rust functions as Python modules.
3. **Port data structures**
   - Implement core vector and matrix operations in Rust, mirroring NumPy array layouts when possible.
   - Provide conversions between `ndarray` (Rust) and `numpy` arrays.
4. **Rewrite contact and constraint routines**
   - Replace existing Numba-accelerated functions with Rust equivalents.
   - Verify numerical consistency using current unit tests.
5. **Iterate on rods and time stepping**
   - Gradually move rod update kernels to Rust, keeping Python orchestration code intact.
   - Expose simple Python wrappers so the public API remains unchanged.
6. **Benchmark and optimize**
   - Measure performance against the Numba versions.
   - Optimize memory usage and explore parallelism (e.g., Rayon) where appropriate.
7. **Documentation and examples**
   - Add build instructions for the Rust extension.
   - Provide example scripts demonstrating usage with the new bindings.

## Long term tasks

- Explore GPU acceleration via libraries such as `wgpu` or `cuda` bindings if needed.
- Maintain feature parity with the Python implementation throughout the rewrite.
- Deprecate Numba code once stability of the Rust core is confirmed.

