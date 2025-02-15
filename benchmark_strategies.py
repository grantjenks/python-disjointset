#!/usr/bin/env python3
import time
import random
import matplotlib.pyplot as plt
import numpy as np

##############################
# Union‐Find Implementations #
##############################


class UnionFindFull:
    """Union‐Find with full (recursive) path compression."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)
        if rootX == rootY:
            return
        if self.rank[rootX] < self.rank[rootY]:
            self.parent[rootX] = rootY
        elif self.rank[rootX] > self.rank[rootY]:
            self.parent[rootY] = rootX
        else:
            self.parent[rootY] = rootX
            self.rank[rootX] += 1


class UnionFindHalving:
    """Union‐Find with path halving (iteratively makes nodes point to their grandparent)."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            # Point x to its grandparent.
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)
        if rootX == rootY:
            return
        if self.rank[rootX] < self.rank[rootY]:
            self.parent[rootX] = rootY
        elif self.rank[rootX] > self.rank[rootY]:
            self.parent[rootY] = rootX
        else:
            self.parent[rootY] = rootX
            self.rank[rootX] += 1


class UnionFindSplitting:
    """Union‐Find with path splitting (each node along the find path points to its grandparent)."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            temp = x
            x = self.parent[x]
            self.parent[temp] = self.parent[x]
        return x

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)
        if rootX == rootY:
            return
        if self.rank[rootX] < self.rank[rootY]:
            self.parent[rootX] = rootY
        elif self.rank[rootX] > self.rank[rootY]:
            self.parent[rootY] = rootX
        else:
            self.parent[rootY] = rootX
            self.rank[rootX] += 1


####################################
# Workload Generation and Running  #
####################################


def generate_workload(union_ratio, n, total_ops):
    """
    Generates a list of operations.
    Each operation is a tuple:
      ("union", a, b)  or  ("find", a)
    union_ratio is the fraction of operations that are unions.
    The remaining operations are finds.
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


def run_workload(uf, operations):
    """
    Executes the list of operations on the given union-find instance uf.
    """
    for op in operations:
        if op[0] == 'union':
            uf.union(op[1], op[2])
        elif op[0] == 'find':
            uf.find(op[1])


###############################
# Benchmark and Plot Function #
###############################


def main():
    # Parameters for the simulation.
    n = 10000  # Number of elements in Union-Find.
    total_ops = 100000  # Total number of operations per workload.

    # Define five workload scenarios with different union:find ratios.
    scenarios = {
        'Union Heavy': 0.999,
        'Union Bias': 0.9,  # 90% union, 10% find
        'Mixed': 0.5,  # 50% union, 50% find
        'Find Bias': 0.1,  # 10% union, 90% find
        'Find Heavy': 0.001,
    }

    # Define the union-find variants to test.
    variants = {
        'Full': UnionFindFull,
        'Halving': UnionFindHalving,
        'Splitting': UnionFindSplitting,
    }

    # For reproducibility, fix the random seed.
    random.seed(42)

    # Dictionary to hold the results:
    # results[scenario][variant] = duration in seconds.
    results = {scenario: {} for scenario in scenarios}

    # For each scenario, generate a fixed workload and run all variants on it.
    for scenario, union_ratio in scenarios.items():
        print(f'Running workload: {scenario}')
        # Generate the operation sequence for this scenario.
        ops = generate_workload(union_ratio, n, total_ops)

        for variant_name, uf_class in variants.items():
            # Create a new instance for each run.
            uf = uf_class(n)
            start = time.perf_counter()
            run_workload(uf, ops)
            duration = time.perf_counter() - start
            results[scenario][variant_name] = duration
            print(f'  {variant_name:8s}: {duration:.4f} seconds')

    # Display the results in a grouped bar chart.
    plot_results(results, list(variants.keys()))


def plot_results(results, variant_names):
    # Extract the scenario names.
    scenarios = list(results.keys())
    num_scenarios = len(scenarios)
    num_variants = len(variant_names)

    # Prepare data: for each variant, a list of times for each scenario.
    data = {variant: [] for variant in variant_names}
    for scenario in scenarios:
        for variant in variant_names:
            data[variant].append(results[scenario][variant])

    # Set up the bar chart.
    x = np.arange(num_scenarios)  # the label locations
    width = 0.25  # the width of the bars
    fig, ax = plt.subplots(figsize=(8, 6))

    # Create one set of bars for each variant.
    for i, variant in enumerate(variant_names):
        ax.bar(x + i * width, data[variant], width, label=variant)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Union-Find Benchmark by Workload Scenario')
    ax.set_xticks(x + width * (num_variants - 1) / 2)
    ax.set_xticklabels(scenarios)
    ax.legend()

    # Annotate bars with their height (optional)
    for i, variant in enumerate(variant_names):
        for j, val in enumerate(data[variant]):
            ax.text(
                x[j] + i * width,
                val,
                f'{val:.3f}',
                ha='center',
                va='bottom',
                fontsize=8,
            )

    plt.tight_layout()
    plt.savefig('plot-strategies.png')
    plt.show()


if __name__ == '__main__':
    main()
