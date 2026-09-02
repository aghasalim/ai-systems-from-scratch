package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

func main() {
	root := "."
	if len(os.Args) > 1 {
		root = os.Args[1]
	}

	readmeBytes, err := os.ReadFile(filepath.Join(root, "README.md"))
	if err != nil {
		fmt.Fprintf(os.Stderr, "cannot read README: %v\n", err)
		os.Exit(1)
	}
	readme := string(readmeBytes)

	f, err := os.Open(filepath.Join(root, "verify", "claims.tsv"))
	if err != nil {
		fmt.Fprintf(os.Stderr, "cannot read claims.tsv: %v\n", err)
		os.Exit(1)
	}
	defer f.Close()

	sc := bufio.NewScanner(f)
	sc.Scan()
	hdr := strings.Split(sc.Text(), "\t")
	col := make(map[string]int)
	for i, h := range hdr {
		col[h] = i
	}

	bad := 0
	rows := 0
	for sc.Scan() {
		line := sc.Text()
		if line == "" {
			continue
		}
		fld := strings.Split(line, "\t")
		rows++

		a, _ := strconv.ParseFloat(fld[col["a"]], 64)
		bStr := fld[col["b"]]
		pub, _ := strconv.ParseFloat(fld[col["published"]], 64)
		rule := fld[col["rule"]]
		id := fld[col["id"]]
		phrase := fld[col["phrase"]]

		var got float64
		switch rule {
		case "copy":
			got = a
		case "round0":
			got = math.Round(a)
		case "round1":
			got = math.Round(a*10) / 10
		case "round2":
			got = math.Round(a*100) / 100
		case "ratio0":
			b, _ := strconv.ParseFloat(bStr, 64)
			got = math.Round(a / b)
		case "ratio1":
			b, _ := strconv.ParseFloat(bStr, 64)
			got = math.Round(a/b*10) / 10
		default:
			fmt.Printf("  FAIL: unknown rule %s\n", rule)
			bad++
			continue
		}

		if math.Abs(got-pub) > 1e-9 {
			fmt.Printf("  FAIL: %s: published %g, recomputed %g\n", id, pub, got)
			bad++
		}

		if !strings.Contains(readme, phrase) {
			fmt.Printf("  FAIL: %s: phrase not in README\n", id)
			bad++
		}
	}

	if bad > 0 {
		fmt.Printf("Go: %d problem(s)\n", bad)
		os.Exit(1)
	}
	fmt.Printf("Go: %d values reproduced, all phrases found in README\n", rows)
}
