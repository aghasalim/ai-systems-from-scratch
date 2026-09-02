import csv, sys, os

root = sys.argv[1] if len(sys.argv) > 1 else "."
readme = open(os.path.join(root, "README.md"), encoding="utf-8").read()

bad = 0
rows = 0
with open(os.path.join(root, "verify", "claims.tsv"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        rows += 1
        a = float(r["a"])
        b = float(r["b"]) if r["b"] != "-" else None
        pub = float(r["published"])
        rule = r["rule"]

        if rule == "copy":
            got = a
        elif rule == "round0":
            got = round(a)
        elif rule == "round1":
            got = round(a, 1)
        elif rule == "round2":
            got = round(a, 2)
        elif rule == "ratio0":
            got = round(a / b)
        elif rule == "ratio1":
            got = round(a / b, 1)
        else:
            print(f"  FAIL: unknown rule {rule}")
            bad += 1
            continue

        if abs(got - pub) > 1e-9:
            print(f"  FAIL: {r['id']}: published {pub}, recomputed {got}")
            bad += 1

        if r["phrase"] not in readme:
            print(f"  FAIL: {r['id']}: phrase not in README")
            bad += 1

if bad:
    print(f"Python: {bad} problem(s)")
    sys.exit(1)
print(f"Python: {rows} values reproduced, all phrases found in README")
