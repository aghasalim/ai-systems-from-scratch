-- Recompute every published value in verify/claims.tsv with SQLite.
.mode tabs
.import verify/claims.tsv claims_raw
.headers off

CREATE TEMP VIEW claims AS
SELECT
  "id" AS id,
  "rule" AS rule,
  CAST("a" AS REAL) AS a,
  CASE WHEN "b" = '-' THEN NULL ELSE CAST("b" AS REAL) END AS b,
  CAST("published" AS REAL) AS published,
  "phrase" AS phrase
FROM claims_raw;

CREATE TEMP VIEW recomputed AS
SELECT id, rule, published, phrase,
  CASE
    WHEN rule = 'copy'   THEN a
    WHEN rule = 'round0' THEN round(a, 0)
    WHEN rule = 'round1' THEN round(a, 1)
    WHEN rule = 'round2' THEN round(a, 2)
    WHEN rule = 'ratio0' THEN round(a / b, 0)
    WHEN rule = 'ratio1' THEN round(a / b, 1)
  END AS got
FROM claims;

.mode csv
SELECT 'DISAGREE', id, rule, published, got
FROM recomputed
WHERE got IS NULL OR abs(got - published) > 1e-12;

SELECT 'ROWS', count(*) FROM recomputed;
SELECT 'BADROWS', count(*) FROM recomputed
WHERE got IS NULL OR abs(got - published) > 1e-12;
