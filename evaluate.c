/* evaluate.c - exact error metrics for 16-bit approximate adders.
 * Tries EVERY pair (a, b) from 0..65535 (4,294,967,296 pairs).
 *
 * Build:  gcc -O2 -fopenmp evaluate.c -o evaluate -lm
 * Run:    ./evaluate trua 5      (truncated adder, k = 5)
 *         ./evaluate loa 6       (lower-part-OR adder, k = 6)
 *         ./evaluate esa 8       (equal-segmentation adder, segment size 8)
 * Prints one line:  design,k,ER_percent,MED,NMED,MRED,MSE
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

#define WIDTH 16
#define N (1u << WIDTH)      /* 65536 possible values for each input   */
#define MAXOUT 131070.0      /* biggest exact sum: 65535 + 65535       */

static uint32_t trua(uint32_t a, uint32_t b, int k) {
    return ((a >> k) + (b >> k)) << k;
}

static uint32_t loa(uint32_t a, uint32_t b, int k) {
    uint32_t low_mask = (1u << k) - 1u;
    uint32_t low = (a | b) & low_mask;
    uint32_t carry_in = (a >> (k - 1)) & (b >> (k - 1)) & 1u;
    uint32_t high = (a >> k) + (b >> k) + carry_in;
    return (high << k) | low;
}

static uint32_t esa(uint32_t a, uint32_t b, int s) {
    uint32_t result = 0;
    int pos = 0;
    while (pos < WIDTH) {
        int bits = (s < WIDTH - pos) ? s : (WIDTH - pos);
        uint32_t mask = (1u << bits) - 1u;
        uint32_t total = ((a >> pos) & mask) + ((b >> pos) & mask);
        if (pos + bits < WIDTH) total &= mask;   /* drop carry between segments */
        result |= total << pos;
        pos += bits;
    }
    return result;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "usage: %s trua|loa|esa K\n", argv[0]);
        return 1;
    }
    int type;
    if (strcmp(argv[1], "trua") == 0)     type = 0;
    else if (strcmp(argv[1], "loa") == 0) type = 1;
    else if (strcmp(argv[1], "esa") == 0) type = 2;
    else { fprintf(stderr, "unknown design '%s'\n", argv[1]); return 1; }
    int k = atoi(argv[2]);
    if (k < 1 || k > 15) { fprintf(stderr, "K must be 1..15\n"); return 1; }

    long long n_wrong = 0, n_red = 0;
    double sum_ed = 0.0, sum_sq = 0.0, sum_red = 0.0;

    /* OpenMP splits the loop over 'a' across all your CPU cores. */
    #pragma omp parallel for reduction(+:n_wrong, n_red, sum_ed, sum_sq, sum_red) schedule(static)
    for (int a = 0; a < (int)N; a++) {
        long long w = 0, r = 0;
        double ed_sum = 0.0, sq_sum = 0.0, red_sum = 0.0;
        for (uint32_t b = 0; b < N; b++) {
            uint32_t y = (uint32_t)a + b;                       /* exact sum  */
            uint32_t yh = (type == 0) ? trua((uint32_t)a, b, k)
                        : (type == 1) ? loa((uint32_t)a, b, k)
                        :               esa((uint32_t)a, b, k); /* approx sum */
            double ed = fabs((double)yh - (double)y);           /* error distance */
            if (ed > 0.0) w++;
            ed_sum += ed;
            sq_sum += ed * ed;
            if (y > 0) { red_sum += ed / (double)y; r++; }      /* skip a=b=0 */
        }
        n_wrong += w; n_red += r;
        sum_ed += ed_sum; sum_sq += sq_sum; sum_red += red_sum;
    }

    double total = (double)N * (double)N;
    double er   = 100.0 * (double)n_wrong / total;
    double med  = sum_ed / total;
    double nmed = med / MAXOUT;
    double mred = sum_red / (double)n_red;
    double mse  = sum_sq / total;
    printf("%s,%d,%.4f,%.6f,%.6e,%.6e,%.6e\n", argv[1], k, er, med, nmed, mred, mse);
    return 0;
}
