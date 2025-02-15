# disjointset

disjointset is a high-performance C extension module for Python that implements the union–find (disjoint set) data structure. Designed with versatility in mind, the module provides two primary variants of the disjoint set abstraction:

- **StaticDisjointSet:**
  Pre-allocates storage for a fixed number of elements (0 to n−1) and is optimized for integer indices. It uses efficient array‐based structures and path‐splitting (a form of path compression) to achieve near‑constant operation times.

- **DynamicDisjointSet:**
  Supports arbitrary hashable objects by dynamically creating new entries as needed. Under the hood, it leverages Python dictionaries rather than pre‐allocated lists. This provides greater flexibility at the slight expense of performance.

Both variants support standard union–find operations including `find`, `union`, `match` (to check connectivity), and `sets` (to extract connected components).

## Features

- **Efficient Union–Find Implementation:**
  Uses union by rank together with an aggressive path compression strategy (specifically, path splitting) to minimize the cost of union and find operations.

- **Two Variants for Different Use Cases:**
  - **StaticDisjointSet:** Best suited when the universe of elements is known in advance.
  - **DynamicDisjointSet:** Ideal for applications requiring support for arbitrary objects, created on the fly.

- **Easy-to-Use API:**
  A simple factory constructor is provided. Call `fastdisjointset.DisjointSet(n)` (with an integer) to obtain a static variant or `fastdisjointset.DisjointSet()` (no argument) to get the dynamic variant.

- **Benchmarking and Testing:**
  Comprehensive benchmarks measure the performance of both the underlying strategies and implementations. Detailed plots are generated during benchmarking and can be viewed via the provided links.

## Benchmarks

This project includes two sets of benchmarks that illustrate the performance characteristics and tradeoffs of the union–find implementations.

### Strategies Benchmark

The **strategies benchmark** compares three different path compression approaches implemented with union by rank:

1. **Full Path Compression:**
   Uses recursion to update every node on the path from a given element to its root. While effective at flattening the tree, the recursive overhead can be more costly in practice.

2. **Path Halving:**
   Iteratively updates every other node (by making each node point to its grandparent) during a find. This method reduces overhead and improves iteration time compared to full compression.

3. **Path Splitting:**
   Iteratively updates every node along the find path so that each one points to its grandparent.

![plot strategies](https://github.com/grantjenks/python-disjointset/blob/main/plot-strategies.png?raw=true)

As demonstrated in the plot, path splitting is consistently the fastest option among the three due to its minimal per-operation overhead and effective tree flattening.

These benchmarks use a series of simulated operations designed to stress different aspects (union-heavy, find-heavy, and balanced workloads) of the union–find implementation. The grouped bar chart provided in the benchmark plot clearly shows that the **path splitting** strategy outperforms the other approaches in a variety of scenarios.

### Disjointset Benchmark

In addition to multiple strategies for path compression, the project benchmarks the two disjoint set variants:

- **StaticDisjointSet (List-based Implementation):**
  Uses pre-allocated lists for storing parent and rank information. This approach is highly efficient when the number of elements is fixed and known in advance. Its use of raw arrays minimizes overhead and maximizes speed.

- **DynamicDisjointSet (Dict-based Implementation):**
  Relies on Python dictionaries, which allow for dynamic key insertion and support arbitrary objects. Although the dictionary-based approach is slightly slower on a per-operation basis because of hashing and dynamic memory management, it offers flexibility for cases when the element universe is not predetermined.

![benchmark plot](https://github.com/grantjenks/python-disjointset/blob/main/plot-disjointset.png?raw=true)

The benchmark plot for the fastdisjointset implementation illustrates the tradeoffs between these methods. The static variant shows superior performance when high throughput is needed and the element domain is fixed, while the dynamic variant is invaluable for more flexible or heterogeneous data applications.

## Installation

Install fastdisjointset using pip:

```bash
python -m pip install fastdisjointset
```

Alternatively, clone the repository and install in editable mode:

```bash
git clone https://github.com/grantjenks/python-disjointset.git
cd python-disjointset
python -m pip install -e .
```

> **Note:** As fastdisjointset is a C extension module, you will need a C compiler and the Python development headers installed on your system.

## Usage Example

Below is an example demonstrating how to use fastdisjointset in both static and dynamic modes:

```python
import fastdisjointset

# StaticDisjointSet: Create a disjoint set for 10 elements (0 through 9).
ds_static = fastdisjointset.DisjointSet(10)
ds_static.union(1, 2)
ds_static.union(2, 3)
print("Static: Are 1 and 3 connected?", ds_static.find(1) == ds_static.find(3))  # Expected output: True

# DynamicDisjointSet: No predefined count; supports arbitrary objects.
ds_dynamic = fastdisjointset.DisjointSet()
ds_dynamic.union('apple', 'banana')
ds_dynamic.union('banana', 'cherry')
print("Dynamic: Are 'apple' and 'cherry' connected?", ds_dynamic.find('apple') == ds_dynamic.find('cherry'))  # Expected output: True

# Getting the groups (sets) of connected nodes.
print("Static groups:", ds_static.sets())
print("Dynamic groups:", ds_dynamic.sets())
```

## Benchmarking

For performance analysis, two benchmarking scripts are provided:

- **benchmark_strategies.py:**
  This script compares the three union–find path compression techniques: full path compression, path halving, and path splitting. The results, clearly showing that path splitting is the fastest, are summarized in a grouped bar chart.

- **benchmark_disjointset.py:**
  This benchmark tests the overall disjoint set implementations by running a series of union and find operations across multiple simulated workloads (e.g., union-heavy, mixed, find-heavy). It compares the static (list-based) and dynamic (dict-based) implementations, illustrating the tradeoffs between performance and flexibility.

To run the benchmarks, execute:

```bash
python benchmark_strategies.py
python benchmark_disjointset.py
```

Each script will generate and display a bar chart summarizing the results.

## Development & Continuous Integration

To develop and test fastdisjointset locally:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/grantjenks/python-disjointset.git
   cd python-disjointset
   ```

2. **Build and install in editable mode:**

   ```bash
   python -m pip install -e .
   ```

3. **Run tests:**

   ```bash
   python test_disjointset.py
   ```

This project leverages GitHub Actions for continuous integration, which runs tests across multiple Python versions and operating systems, checks linting using ruff, and builds wheels for distribution.

## License

fastdisjointset is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for full details.
