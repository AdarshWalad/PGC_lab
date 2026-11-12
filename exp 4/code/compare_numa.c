/*
 * compare_numa.c
 *
 * Combines false-sharing benchmark and memory-sweep benchmark
 * into a single program for easy side-by-side comparison.
 *
 * Compile:
 *   gcc -O2 compare_numa.c -fopenmp -o compare_numa
 *
 * Run:
 *   ./compare_numa
 *   numactl --cpunodebind=0 --membind=0 ./compare_numa
 *   numactl --cpunodebind=0 --membind=1 ./compare_numa
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <omp.h>

/* ------------------------------------------------------------------ */
/*  False-sharing benchmark                                            */
/* ------------------------------------------------------------------ */
#define FS_ITERATIONS 100000000UL
#define CACHE_LINE     64

typedef struct { long counter[2];                              } adj_t;
typedef struct { long counter; char pad[CACHE_LINE-sizeof(long)]; } pad_entry_t;
typedef struct { pad_entry_t entry[2];                         } pad_t;

static void bench_false_sharing(int threads, const char *layout)
{
    omp_set_num_threads(threads);
    long total = 0;
    double t0, t1;
    int correct;

    if (strcmp(layout, "adjacent") == 0) {
        adj_t adj = { .counter = {0, 0} };
        t0 = omp_get_wtime();
        #pragma omp parallel for schedule(static) reduction(+:total)
        for (unsigned long i = 0; i < FS_ITERATIONS; i++)
            adj.counter[omp_get_thread_num() % 2]++;
        t1 = omp_get_wtime();
        for (int i = 0; i < 2; i++) total += adj.counter[i];
    } else {
        pad_t p; memset(&p, 0, sizeof(p));
        t0 = omp_get_wtime();
        #pragma omp parallel for schedule(static) reduction(+:total)
        for (unsigned long i = 0; i < FS_ITERATIONS; i++)
            p.entry[omp_get_thread_num() % 2].counter++;
        t1 = omp_get_wtime();
        for (int i = 0; i < 2; i++) total += p.entry[i].counter;
    }

    correct = (total == (long)FS_ITERATIONS);
    printf("%-10s | %7d | %11ld | %-9s | %.4f\n",
           layout, threads, total,
           correct ? "Correct" : "WRONG",
           t1 - t0);
}

/* ------------------------------------------------------------------ */
/*  Memory-sweep benchmark                                             */
/* ------------------------------------------------------------------ */
#define SWEEP_MB    512UL
#define SWEEP_PASSES  4
#define MB_BYTES    (1UL << 20)

static void bench_memory_sweep(int threads)
{
    omp_set_num_threads(threads);
    size_t n = (SWEEP_MB * MB_BYTES) / sizeof(uint64_t);
    uint64_t *buf = malloc(n * sizeof(uint64_t));
    if (!buf) { perror("malloc"); return; }

    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; i++) buf[i] = i;

    uint64_t sum = 0;
    double t0 = omp_get_wtime();
    for (int p = 0; p < SWEEP_PASSES; p++) {
        #pragma omp parallel for schedule(static) reduction(+:sum)
        for (size_t i = 0; i < n; i++) sum += buf[i];
    }
    double t1 = omp_get_wtime();
    free(buf);

    printf("%7d | %.4f\n", threads, t1 - t0);
}

/* ------------------------------------------------------------------ */
/*  main                                                               */
/* ------------------------------------------------------------------ */
int main(void)
{
    int thread_counts[] = {1, 2, 4};
    int n_tc = sizeof(thread_counts) / sizeof(thread_counts[0]);

    /* Table 1: False sharing */
    printf("Table 1: false sharing (100000000 increments in total)\n");
    printf("%-10s | %7s | %11s | %-9s | %s\n",
           "Layout", "Threads", "Final Count", "Correctness", "Time (s)");
    printf("------------------------------------------------------------\n");

    for (int t = 0; t < n_tc; t++) {
        bench_false_sharing(thread_counts[t], "adjacent");
        bench_false_sharing(thread_counts[t], "padded");
        printf("------------------------------------------------------------\n");
    }

    /* Table 2: Memory sweep */
    printf("\nTable 2: memory sweep of %lu MB (%d passes)\n", SWEEP_MB, SWEEP_PASSES);
    printf("%7s | %s\n", "Threads", "Time (s)");
    printf("--------------------\n");
    for (int t = 0; t < 2; t++)   /* only 1 and 2 threads shown */
        bench_memory_sweep(thread_counts[t]);

    return 0;
}
