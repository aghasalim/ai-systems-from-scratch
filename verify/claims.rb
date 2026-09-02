# frozen_string_literal: true

require "csv"

root = ARGV[0] || "."
readme = File.read(File.join(root, "README.md"), encoding: "UTF-8")
tsv = CSV.read(File.join(root, "verify", "claims.tsv"), col_sep: "\t", headers: true)

bad = 0
tsv.each do |r|
  a = r["a"].to_f
  b_val = r["b"] == "-" ? nil : r["b"].to_f
  pub = r["published"].to_f
  rule = r["rule"]

  got = case rule
        when "copy"   then a
        when "round0" then a.round(0).to_f
        when "round1" then a.round(1)
        when "round2" then a.round(2)
        when "ratio0" then (a / b_val).round(0).to_f
        when "ratio1" then (a / b_val).round(1)
        else
          puts "  FAIL: unknown rule #{rule}"
          bad += 1
          next
        end

  if (got - pub).abs > 1e-9
    puts "  FAIL: #{r['id']}: published #{pub}, recomputed #{got}"
    bad += 1
  end

  unless readme.include?(r["phrase"])
    puts "  FAIL: #{r['id']}: phrase not in README"
    bad += 1
  end
end

if bad > 0
  puts "Ruby: #{bad} problem(s)"
  exit 1
end
puts "Ruby: #{tsv.size} values reproduced, all phrases found in README"
