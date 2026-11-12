/*
 * false_sharing.c
 *
 * Demonstrates false sharing and its elimination using padding.
 *
 * Compile:
 *   gcc -O2 false_sharing.c -fopenmp -o false_sharing
 *
 * Run:
 *   OMP_NUM_THREADS=2 ./false_sharing adjacent
 *   OMP_NUM_THREADS=2 ./false_sharing padded
 *   OMP_NUM_THREADS=4 ./false_sharing adjacent
 *   OMP_NUM_THREADS=4 ./false_sharing padded
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

#define ITERATIONS 100000000UL
#define CACHE_LINE  64

/* Adjacent layout – counters packed together, causing false sharing */
typedef struct {
    long counter[2];
} adjacent_t;

/* Padded layout – each counter on its own cache line */
typedef struct {
    long counter;
    char pad[CACHE_LINE - sizeof(long)];
} padded_entry_t;

typedef struct {
    padded_entry_t entry[2];
} padded_t;

int main(int argc, char *argv[])
{
    const char *layout = (argc > 1) ? argv[1] : "adjacent";
    int use_padded = (strcmp(layout, "padded") == 0);

    int nthreads = omp_get_max_threads();
    long total = 0;
    double t_start, t_end;

    if (!use_padded) {
        /* Adjacent: false sharing */
        adjacent_t adj = { .counter = {0, 0} };

        t_start = omp_get_wtime();
        #pragma omp parallel for schedule(static) reduction(+:total)
        for (unsigned long i = 0; i < ITERATIONS; i++) {
            int tid = omp_get_thread_num() % 2;
            adj.counter[tid]++;
        }
        t_end = omp_get_wtime();

        for (int i = 0; i < 2; i++) total += adj.counter[i];
        printf("adjacent | threads=%d | total=%ld | time=%.4f s\n",
               nthreads, total, t_end - t_start);

    } else {
        /* Padded: no false sharing */
        padded_t pad;
        memset(&pad, 0, sizeof(pad));

        t_start = omp_get_wtime();
        #pragma omp parallel for schedule(static) reduction(+:total)
        for (unsigned long i = 0; i < ITERATIONS; i++) {
            int tid = omp_get_thread_num() % 2;
            pad.entry[tid].counter++;
        }
        t_end = omp_get_wtime();

        for (int i = 0; i < 2; i++) total += pad.entry[i].counter;
        printf("padded   | threads=%d | total=%ld | time=%.4f s\n",
               nthreads, total, t_end - t_start);
    }

    return 0;
}
