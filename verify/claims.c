/* Recompute every published value in verify/claims.tsv in C, and check that
 * each claim phrase appears in the README.
 *
 * Build: cc -std=c99 -O2 -Wall -o claimc verify/claims.c -lm
 * Run:   ./claimc <repo root>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAXCOL 16
#define MAXLINE 2048

static int problems = 0;
static void fail(const char *m) { printf("  FAIL: %s\n", m); problems++; }

static char *slurp(const char *path) {
    FILE *f = fopen(path, "rb");
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    rewind(f);
    char *b = malloc((size_t)n + 1);
    fread(b, 1, (size_t)n, f);
    b[n] = '\0';
    fclose(f);
    return b;
}

static int find_col(char *hdr[], int n, const char *name) {
    for (int i = 0; i < n; i++)
        if (strcmp(hdr[i], name) == 0) return i;
    fprintf(stderr, "no column %s\n", name);
    exit(1);
}

static int split_tab(char *line, char *out[], int max) {
    int n = 0;
    out[n++] = line;
    while (*line) {
        if (*line == '\t') {
            *line = '\0';
            if (n < max) out[n++] = line + 1;
        }
        line++;
    }
    return n;
}

int main(int argc, char **argv) {
    const char *root = argc > 1 ? argv[1] : ".";
    char path[512];

    snprintf(path, sizeof path, "%s/README.md", root);
    char *readme = slurp(path);
    if (!readme) { fprintf(stderr, "cannot read %s\n", path); return 1; }

    snprintf(path, sizeof path, "%s/verify/claims.tsv", root);
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "cannot read %s\n", path); return 1; }

    char line[MAXLINE];
    char *cols[MAXCOL];
    fgets(line, sizeof line, f);
    line[strcspn(line, "\r\n")] = '\0';
    int ncols = split_tab(line, cols, MAXCOL);
    int ci = find_col(cols, ncols, "id");
    int cr = find_col(cols, ncols, "rule");
    int ca = find_col(cols, ncols, "a");
    int cb = find_col(cols, ncols, "b");
    int cp = find_col(cols, ncols, "published");
    int cph = find_col(cols, ncols, "phrase");

    int rows = 0;
    double worst = 0;
    while (fgets(line, sizeof line, f)) {
        line[strcspn(line, "\r\n")] = '\0';
        if (!*line) continue;
        char *fld[MAXCOL];
        split_tab(line, fld, MAXCOL);
        rows++;

        double a = atof(fld[ca]);
        double b_val = (strcmp(fld[cb], "-") == 0) ? 0 : atof(fld[cb]);
        double pub = atof(fld[cp]);
        const char *rule = fld[cr];
        double got;

        if (strcmp(rule, "copy") == 0) got = a;
        else if (strcmp(rule, "round0") == 0) got = round(a);
        else if (strcmp(rule, "round1") == 0) got = round(a * 10) / 10;
        else if (strcmp(rule, "round2") == 0) got = round(a * 100) / 100;
        else if (strcmp(rule, "ratio0") == 0) got = round(a / b_val);
        else if (strcmp(rule, "ratio1") == 0) got = round(a / b_val * 10) / 10;
        else { char m[256]; snprintf(m, sizeof m, "unknown rule %s", rule); fail(m); continue; }

        double err = fabs(got - pub);
        if (err > 1e-9) {
            char m[256];
            snprintf(m, sizeof m, "%s: published %.4f, recomputed %.4f", fld[ci], pub, got);
            fail(m);
        }
        if (err > worst) worst = err;

        if (!strstr(readme, fld[cph])) {
            char m[512];
            snprintf(m, sizeof m, "%s: phrase '%s' not found in README", fld[ci], fld[cph]);
            fail(m);
        }
    }
    fclose(f);
    free(readme);

    if (problems) {
        printf("C: %d problem(s)\n", problems);
        return 1;
    }
    printf("C: %d values reproduced, largest error %.1e, all phrases found in README\n", rows, worst);
    return 0;
}
