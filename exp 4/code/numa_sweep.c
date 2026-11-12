/*
 * numa_sweep.c
 *
 * Memory bandwidth sweep to observe NUMA effects.
 * Allocates a large buffer and sweeps through it multiple times
 * measuring throughput with varying thread counts and NUMA policies.
 *
 * Compile:
 *   gcc -O2 numa_sweep.c -fopenmp -o numa_sweep
 *
 * Run:
 *   ./numa_sweep                              (default 512 MB, 4 passes)
 *   OMP_NUM_THREADS=2 ./numa_sweep
 *   ./numa_sweep 512
 *   OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=0 ./numa_sweep
 *   OMP_NUM_THREADS=2 numactl --cpunodebind=0 --membind=1 ./numa_sweep
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <omp.h>

#define PASSES      4
#define MB          (1UL << 20)

int main(int argc, char *argv[])
{
    size_t buf_mb  = (argc > 1) ? (size_t)atol(argv[1]) : 512;
    size_t n_elems = (buf_mb * MB) / sizeof(uint64_t);

    uint64_t *buf = (uint64_t *)malloc(n_elems * sizeof(uint64_t));
    if (!buf) { perror("malloc"); return 1; }

    /* First-touch initialisation – distribute pages across threads */
    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n_elems; i++)
        buf[i] = (uint64_t)i;

    int nthreads = omp_get_max_threads();
    uint64_t sum = 0;
    double t_start = omp_get_wtime();

    for (int p = 0; p < PASSES; p++) {
        #pragma omp parallel for schedule(static) reduction(+:sum)
        for (size_t i = 0; i < n_elems; i++)
            sum += buf[i];
    }

    double t_end = omp_get_wtime();
    free(buf);

    printf("buffer=%zu MB | threads=%d | sum=%lu | time=%.4f s\n",
           buf_mb, nthreads, (unsigned long)(sum & 0xFFFFFFFF), t_end - t_start);

    return 0;
}
