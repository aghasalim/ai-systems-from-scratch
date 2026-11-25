# The rules every repository follows

1. I write a reference implementation before the optimised one.
2. I never loosen a tolerance just to make a test pass.
3. I use relative tolerance over absolute. The bar is "no worse than the naive
   implementation in the same precision".
4. Every number comes from a measurement. I don't take numbers from the paper,
   estimate them from the algorithm, or round them by feel.
5. I report variance along with the point estimate, with at least three seeds for
   anything that involves training.
6. Negative results stay in. I wouldn't believe an ablation table with only wins
   in it.
7. I write "not measured on this hardware" instead of extrapolating.

Rules 6 and 7 mattered a lot in practice. Four of the eight repositories have a
result that makes the thing I built look worse. One has a claim I made and then
had to take back after I checked its error bar.
