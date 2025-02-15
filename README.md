# disjointset

disjointset is a high-performance C extension module for Python that implements the union–find (disjoint set) data structure. Designed with versatility in mind, the module provides two primary variants of the disjoint set abstraction:

- **StaticDisjointSet:**
  Pre-allocates storage for a fixed number of elements (0 to n−1) and is optimized for integer indices. It uses efficient array-based structures and path-splitting for almost constant time operations.

- **DynamicDisjointSet:**
  Supports arbitrary hashable objects by dynamically creating new entries as needed. Behind the scenes, it leverages Python dictionaries to implement union–find operations with the same efficient path-splitting strategy.

Both variants support standard union–find operations including `find`, `union`, `match` (to check connectivity), and `sets` (to extract the connected components).

## Features

- **Efficient Union–Find Implementation:**
  Uses union by rank together with path splitting to minimize the cost of both union and find operations.

- **Two Variants for Different Use Cases:**
  - **StaticDisjointSet:** Best suited when the universe of elements is known in advance and represented as a range of integers.
  - **DynamicDisjointSet:** Ideal for working with dynamic or arbitrary keys (such as strings or objects).

- **Easy-to-Use API:**
  A simple factory constructor is provided. Call `disjointset.DisjointSet(n)` (with an integer) to obtain a static variant or `disjointset.DisjointSet(None)` (or no argument) for the dynamic variant.

- **Benchmarking and Testing:**
  Comes with benchmarking scripts (e.g., `benchmark_disjointset.py` and `benchmark_strategies.py`) and unit tests (`test_disjointset.py`) to validate performance and correctness.

- **CI/CD Integration:**
  This project uses GitHub Actions to run tests, build wheels across multiple platforms, and publish releases automatically.

## Installation

Install disjointset using pip:

```bash
python -m pip install disjointset
```

> Note: Since disjointset is a C extension module, you will need a C compiler and the Python development headers installed on your system.

Alternatively, clone the repository and install in editable mode:

```bash
git clone https://github.com/grantjenks/python-disjointset.git
cd python-disjointset
python -m pip install -e .
```

## Usage Example

Below is an example demonstrating how to use disjointset in both static and dynamic modes:

```python
import disjointset

# StaticDisjointSet: Create a disjoint set for 10 elements (0 through 9).
ds_static = disjointset.DisjointSet(10)
ds_static.union(1, 2)
ds_static.union(2, 3)
print("Static: Are 1 and 3 connected?",
      ds_static.find(1) == ds_static.find(3))  # Expected output: True

# DynamicDisjointSet: No predefined count; supports arbitrary objects.
ds_dynamic = disjointset.DisjointSet()
ds_dynamic.union('apple', 'banana')
ds_dynamic.union('banana', 'cherry')
print("Dynamic: Are 'apple' and 'cherry' connected?",
      ds_dynamic.find('apple') == ds_dynamic.find('cherry'))  # Expected output: True

# Getting the groups (sets) of connected nodes.
print("Static groups:", ds_static.sets())
print("Dynamic groups:", ds_dynamic.sets())
```

## Benchmarking

For performance analysis, the repository includes benchmarking scripts:

- **benchmark_disjointset.py:**
  Benchmarks the performance of both Static and Dynamic disjoint sets using a variety of union‑find workloads.

- **benchmark_strategies.py:**
  Compares different union–find path compression strategies (full path compression, halving, splitting) on a simulated workload.

Run a benchmark by executing:

```bash
python benchmark_disjointset.py
```

and view the generated plots to compare performance.

## Development & Continuous Integration

To develop and test disjointset locally:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/grantjenks/python-disjointset.git
   cd python-disjointset
   ```

2. **Build and install in editable mode:**

   ```bash
   python -m pip install -e .
   ```

3. **Run the tests:**

   ```bash
   python test_disjointset.py
   ```

This project leverages GitHub Actions for continuous integration, which runs tests across multiple Python versions and operating systems, checks linting using ruff, and builds wheels for distribution.

## License

disjointset is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for full details.
