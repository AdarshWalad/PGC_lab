# Experiment 4 — Source Code Reference

This folder contains the simulation, benchmark, and plotting scripts for **Experiment 4 (Cache Coherence, False Sharing & NUMA Effects)**.

For the full experiment report with embedded graphs and screenshots, see [../README.md](../README.md).

## Files

| File | Language | Purpose |
| :--- | :--- | :--- |
| `coherence_sim.py` | Python | Simulates MSI, MESI, and MOESI protocols under adjacent and padded layouts |
| `false_sharing.c` | C (OpenMP) | Benchmarks false sharing (`adjacent`) vs. cache-line padding (`padded`) |
| `numa_sweep.c` | C (OpenMP) | Sweeps a 512 MB buffer across 4 passes to measure NUMA memory bandwidth |
| `compare_numa.c` | C (OpenMP) | Combined false-sharing + memory-sweep benchmark for side-by-side comparison |
| `plot_graphs.py` | Python (Matplotlib) | Generates all 4 visualization charts into `../graphs/` |

## Quick Commands

```bash
# 1. Run cache coherence simulator
python3 coherence_sim.py 1000

# 2. Compile & run false sharing benchmark
gcc -O2 false_sharing.c -fopenmp -o false_sharing
OMP_NUM_THREADS=2 ./false_sharing adjacent
OMP_NUM_THREADS=2 ./false_sharing padded
OMP_NUM_THREADS=4 ./false_sharing adjacent
OMP_NUM_THREADS=4 ./false_sharing padded

# 3. Compile & run NUMA sweep
gcc -O2 numa_sweep.c -fopenmp -o numa_sweep
./numa_sweep
OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=0 ./numa_sweep

# 4. Compile & run combined comparison
gcc -O2 compare_numa.c -fopenmp -o compare_numa
./compare_numa
numactl --cpunodebind=0 --membind=0 ./compare_numa

# 5. Regenerate graphs
python3 plot_graphs.py
```

## Related Directories

- `../images/` — Terminal execution screenshots (`screenshot1_coherence_sim.jpg`, `screenshot2_false_sharing.png`, `screenshot3_numa_sweep.jpg`, `screenshot4_compare_numa.png`)
- `../graphs/` — Generated visualization charts (`graph1_coherence_protocols.png`, `graph2_false_sharing.png`, `graph3_numa_sweep.png`, `graph4_compare_numa.png`)
