# ai-systems-from-scratch

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23003612.svg)](https://doi.org/10.5281/zenodo.23003612)

I rebuilt eight important pieces of modern AI from the papers. Each one has a
correctness harness, a benchmark, an ablation and a write-up. Every number in
each repository came from a run in that repository. Each repo also has a CI
script that fails the build if the text and the data stop agreeing. The headline
figures in the table below are recomputed from the raw inputs by separate
implementations in `verify/`, and CI fails the build if anything disagrees.

Everything runs on a laptop CPU. I don't think scaling down is cheating here,
since the ablations do most of the work and they still hold at small scale.

| repository | what it establishes | headline result |
|---|---|---|
| [flash-attention](https://github.com/aghasalim/flash-attention-from-scratch) | attention is a memory traffic problem | fusion worth about 3x, throughput 22% to 67% of peak |
| [latent-diffusion](https://github.com/aghasalim/latent-diffusion-from-scratch) | compression before generation | 5.3x faster training, 6.2x better samples at matched steps |
| [rectified-flow](https://github.com/aghasalim/rectified-flow-from-scratch) | straight paths mean cheap sampling | reflow buys 1-step sampling, 128x less compute, no loss |
| [rlhf-ppo](https://github.com/aghasalim/rlhf-ppo-from-scratch) | optimising a proxy has a cost | gold reward peaks then falls below the starting policy |
| [schrodinger-bridge](https://github.com/aghasalim/schrodinger-bridge-from-scratch) | simulation-free beats alternating | bridge matching 1.3x to 12x better at a quarter the cost |
| [mla](https://github.com/aghasalim/mla-from-scratch) | the KV cache is the serving wall | 14.2x cache reduction, 120 GB to 8.4 GB at 128k context |
| [world-model](https://github.com/aghasalim/world-model-from-scratch) | learning inside a learned model | the model works, the agent inside it does not, and I say so |
| [vla](https://github.com/aghasalim/vla-from-scratch) | how a policy should emit an action | a regression head averages two valid routes and drives between them |

## How they connect

The projects are linked, and I picked them with three themes in mind.

The first is memory. In `flash-attention` I fuse the softmax so the score matrix
never gets written to memory, which tackles the problem from the kernel side. In
`mla` I compress the KV cache so there's less to move, which tackles the same
problem through the architecture.

The second is generative paths. `rectified-flow` uses a straight interpolant and
`latent-diffusion` uses a curved one. `schrodinger-bridge` generalises both to
transport between two arbitrary distributions. I did flow matching first on
purpose, because it's simpler, and after that diffusion looks like a special case.
In `vla` the same flow matching objective turns into a robot action head. There
I compare it with a diffusion head mostly on latency.

The third is what optimisation costs. In `rlhf-ppo` a policy exploits an
imperfect reward until the true objective collapses. In `world-model` an agent
learns inside an imperfect model of the world. To me they're the same failure.
In both, something gets optimised hard against a learned approximation of what
you actually want.

## The rules every repository follows

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

## Things that went wrong, and what they cost

I think the logbooks are the most useful files in these repositories. Here are
some of the mistakes from them.

- I reversed a backward drift twice, because the DSB target already includes the
  reversal. Forward loss got to 1.5e11 before I found it.
- My distance metric compared sorted point clouds element by element, which only
  works when the sample sizes are equal. A working run that matched the target
  mean to 0.01 got scored at 3.04, and I went hunting for a transport bug that
  didn't exist.
- My UNet rebuilt skip channel counts that it should have saved, and was off by
  one level. GroupNorm caught it. A plain convolution would have accepted the
  wrong shape and kept training badly.
- I froze a reference policy in place, and every later policy inherited that
  through a deepcopy. So from the second run of a sweep on, nothing was being
  optimised, and nothing told me.
- Twice I read a trend off single-run data, and both times I had to take it back
  once repeats gave it an error bar.
- A train/test split returned fewer objects than a scene needs and left the rest
  at their zero initialised default. That quietly put a training object into the
  held out evaluation set. There was no error and no crash, and a test caught it.

## License

MIT.
