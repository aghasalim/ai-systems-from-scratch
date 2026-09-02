import { readFileSync } from "fs";
import { join } from "path";

const root = process.argv[2] || ".";
const readme = readFileSync(join(root, "README.md"), "utf-8");
const lines = readFileSync(join(root, "verify", "claims.tsv"), "utf-8")
  .trim().split("\n");

const hdr = lines[0].split("\t");
const idx = (n) => hdr.indexOf(n);

let bad = 0;
let rows = 0;
for (let i = 1; i < lines.length; i++) {
  const f = lines[i].split("\t");
  if (!f[0]) continue;
  rows++;
  const a = parseFloat(f[idx("a")]);
  const b = f[idx("b")] === "-" ? null : parseFloat(f[idx("b")]);
  const pub = parseFloat(f[idx("published")]);
  const rule = f[idx("rule")];
  const id = f[idx("id")];
  const phrase = f[idx("phrase")];

  let got;
  if (rule === "copy") got = a;
  else if (rule === "round0") got = Math.round(a);
  else if (rule === "round1") got = Math.round(a * 10) / 10;
  else if (rule === "round2") got = Math.round(a * 100) / 100;
  else if (rule === "ratio0") got = Math.round(a / b);
  else if (rule === "ratio1") got = Math.round(a / b * 10) / 10;
  else { console.log(`  FAIL: unknown rule ${rule}`); bad++; continue; }

  if (Math.abs(got - pub) > 1e-9) {
    console.log(`  FAIL: ${id}: published ${pub}, recomputed ${got}`);
    bad++;
  }
  if (!readme.includes(phrase)) {
    console.log(`  FAIL: ${id}: phrase not in README`);
    bad++;
  }
}

if (bad) {
  console.log(`JS: ${bad} problem(s)`);
  process.exit(1);
}
console.log(`JS: ${rows} values reproduced, all phrases found in README`);
