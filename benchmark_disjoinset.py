#!/usr/bin/env python3
"""
benchmark_disjointset.py

This script benchmarks the performance of the two disjoint-set implementations
provided by the C extension module "disjointset". It compares the performance of:
  - StaticDisjointSet (obtained by calling DisjointSet(n))
  - DynamicDisjointSet (obtained by calling DisjointSet(None))

Five workload scenarios are simulated:
  • Union Heavy (99.9% unions, 0.1% finds)
  • Union Bias (90% unions, 10% finds)
  • Mixed (50% unions, 50% finds)
  • Find Bias (10% unions, 90% finds)
  • Find Heavy (0.1% unions, 99.9% finds)

Operations (union and find) are generated using random integers in the range [0, n-1].
Both implementations are benchmarked using the identical sequence of operations per scenario.
The results are presented as a grouped bar chart using Matplotlib.
"""

import time
import random
import matplotlib.pyplot as plt
import numpy as np
import disjointset  # Imports the C extension module


def generate_workload(union_ratio, n, total_ops):
    """
    Creates a list of operations for the workload.
    Each operation is a tuple:
      ("union", a, b)  or  ("find", a)
    where 'union_ratio' is the fraction of operations that are unions.
    """
    union_count = int(total_ops * union_ratio)
    find_count = total_ops - union_count
    ops = []

    # Generate union operations.
    for _ in range(union_count):
        a = random.randint(0, n - 1)
        b = random.randint(0, n - 1)
        ops.append(('union', a, b))

    # Generate find operations.
    for _ in range(find_count):
        a = random.randint(0, n - 1)
        ops.append(('find', a))

    # Shuffle to mix the operations.
    random.shuffle(ops)
    return ops


def run_workload(ds, operations):
    """
    Executes the list of operations on the given disjoint-set instance ds.
    """
    for op in operations:
        if op[0] == 'union':
            ds.union(op[1], op[2])
        elif op[0] == 'find':
            ds.find(op[1])


def main():
    # Configuration parameters.
    n = 10000  # Number of elements (for static variant)
    total_ops = 100000  # Total number of operations in each workload

    # Workload scenarios defined by union:find ratio.
    scenarios = {
        'Union Heavy': 0.999,  # 99.9% union, 0.1% find
        'Union Bias': 0.9,  # 90% union, 10% find
        'Mixed': 0.5,  # 50% union, 50% find
        'Find Bias': 0.1,  # 10% union, 90% find
        'Find Heavy': 0.001,  # 0.1% union, 99.9% find
    }

    # Define the two variants via factory lambdas:
    # - Static: pass an integer n to DisjointSet() to get a StaticDisjointSet.
    # - Dynamic: pass None to DisjointSet() to get a DynamicDisjointSet.
    variants = {
        'Static': lambda: disjointset.DisjointSet(n),
        'Dynamic': lambda: disjointset.DisjointSet(None),
    }

    # Fix the random seed for reproducibility.
    random.seed(42)

    # Dictionary to collect benchmark results.
    # results[scenario][variant] = duration in seconds.
    results = {scenario: {} for scenario in scenarios}

    print('Benchmarking StaticDisjointSet vs DynamicDisjointSet')
    for scenario, union_ratio in scenarios.items():
        print(f'\nScenario: {scenario}')
        # Generate operations for the current scenario.
        ops = generate_workload(union_ratio, n, total_ops)

        for variant_name, create_fn in variants.items():
            ds = create_fn()
            start = time.perf_counter()
            run_workload(ds, ops)
            duration = time.perf_counter() - start
            results[scenario][variant_name] = duration
            print(f'  {variant_name:8s}: {duration:.4f} seconds')

    # Plot the benchmark results.
    plot_results(results)


def plot_results(results):
    # Extract the list of scenarios and variant names.
    scenarios = list(results.keys())
    variant_names = list(next(iter(results.values())).keys())
    num_scenarios = len(scenarios)
    num_variants = len(variant_names)

    # Prepare data for plotting: Each variant's measured times per scenario.
    data = {variant: [] for variant in variant_names}
    for scenario in scenarios:
        for variant in variant_names:
            data[variant].append(results[scenario][variant])

    # Set up the grouped bar chart.
    x = np.arange(num_scenarios)  # Scenario positions on x-axis
    width = 0.35  # Width of each bar; adjust if more variants are added

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, variant in enumerate(variant_names):
        ax.bar(x + i * width, data[variant], width, label=variant)

    ax.set_ylabel('Time (seconds)')
    ax.set_title('Benchmark: StaticDisjointSet vs DynamicDisjointSet')
    ax.set_xticks(x + width * (num_variants - 1) / 2)
    ax.set_xticklabels(scenarios)
    ax.legend()

    # Optionally annotate the bars with their respective values
    for i, variant in enumerate(variant_names):
        for j, value in enumerate(data[variant]):
            ax.text(
                x[j] + i * width,
                value,
                f'{value:.3f}',
                ha='center',
                va='bottom',
                fontsize=8,
            )

    plt.tight_layout()
    plt.savefig('plot-disjointset.png')
    plt.show()


if __name__ == '__main__':
    main()
