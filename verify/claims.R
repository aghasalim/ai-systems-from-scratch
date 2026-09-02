args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[1] else "."

readme <- readLines(file.path(root, "README.md"), warn = FALSE)
readme_text <- paste(readme, collapse = "\n")

claims <- read.delim(file.path(root, "verify", "claims.tsv"),
                     stringsAsFactors = FALSE, colClasses = "character")

bad <- 0
for (i in seq_len(nrow(claims))) {
  r <- claims[i, ]
  a <- as.numeric(r$a)
  b_val <- if (r$b == "-") NA else as.numeric(r$b)
  pub <- as.numeric(r$published)
  rule <- r$rule

  got <- if (rule == "copy") a
  else if (rule == "round0") round(a, 0)
  else if (rule == "round1") round(a, 1)
  else if (rule == "round2") round(a, 2)
  else if (rule == "ratio0") round(a / b_val, 0)
  else if (rule == "ratio1") round(a / b_val, 1)
  else { cat(sprintf("  FAIL: unknown rule %s\n", rule)); bad <- bad + 1; next }

  if (abs(got - pub) > 1e-9) {
    cat(sprintf("  FAIL: %s: published %s, recomputed %s\n", r$id, pub, got))
    bad <- bad + 1
  }

  if (!grepl(r$phrase, readme_text, fixed = TRUE)) {
    cat(sprintf("  FAIL: %s: phrase not in README\n", r$id))
    bad <- bad + 1
  }
}

if (bad > 0) {
  cat(sprintf("R: %d problem(s)\n", bad))
  quit(status = 1)
}
cat(sprintf("R: %d values reproduced, all phrases found in README\n", nrow(claims)))
