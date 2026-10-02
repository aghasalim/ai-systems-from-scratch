#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
fail=0


# --- SQL ---
printf '%-6s ' SQL
cd "$root"
out=$(sqlite3 < verify/claims.sql 2>&1 | tr -d '\r')
badrows=$(echo "$out" | grep '^BADROWS' | cut -d, -f2)
if [ "$badrows" != "0" ]; then
  echo "FAILED"; echo "$out"; fail=1
else
  total=$(echo "$out" | grep '^ROWS' | cut -d, -f2)
  echo "ok ($total rows, 0 disagree)"
fi

# --- C ---
printf '%-6s ' C
claimc=$(mktemp)
cc -std=c99 -O2 -Wall -o "$claimc" verify/claims.c -lm
"$claimc" "$root" || { fail=1; }
rm -f "$claimc"

# --- Go ---
printf '%-6s ' Go
(cd verify/gocheck && go run . "$root") || { fail=1; }

# --- JS ---
printf '%-6s ' JS
node verify/claims.mjs "$root" || { fail=1; }

# --- Python ---
printf '%-6s ' Python
python3 verify/claims.py "$root" || { fail=1; }

# --- R ---
printf '%-6s ' R
Rscript verify/claims.R "$root" || { fail=1; }

# --- Ruby ---
printf '%-6s ' Ruby
ruby verify/claims.rb "$root" || { fail=1; }

# --- Shell ---
printf '%-6s ' Shell
sh_bad=0
while IFS=$'\t' read -r id repo phrase rule a b published; do
  [ "$id" = "id" ] && continue
  case "$rule" in
    copy)   got="$a" ;;
    round0) got=$(printf '%.0f' "$a") ;;
    round1) got=$(printf '%.1f' "$a") ;;
    round2) got=$(printf '%.2f' "$a") ;;
    ratio0) got=$(printf '%.0f' "$(echo "$a / $b" | bc -l)") ;;
    ratio1) got=$(printf '%.1f' "$(echo "$a / $b" | bc -l)") ;;
    *) echo "FAIL: unknown rule $rule"; sh_bad=1; continue ;;
  esac
  if [ "$got" != "$published" ]; then
    echo "FAIL: $id: published=$published got=$got"
    sh_bad=1
  fi
done < verify/claims.tsv
if [ $sh_bad -ne 0 ]; then fail=1; else echo "Shell: all values match"; fi

exit $fail
