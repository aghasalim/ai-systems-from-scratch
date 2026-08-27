# ai-systems-from-scratch

Eight load-bearing pieces of modern AI, each rebuilt from the papers with a
correctness harness, a benchmark, an ablation and an honest write-up. Every
number in every repository came from a run in that repository, and each one has a
script in CI that fails the build if the prose and the data stop agreeing.

All of it runs on a laptop CPU. Scaling down is not cheating: the ablations are
what carry the work, and they are valid at small scale.

| repository | what it establishes | headline result |
|---|---|---|
| [flash-attention](https://github.com/aghasalim/flash-attention-from-scratch) | attention is a memory traffic problem | fusion worth about 3x, throughput 22% to 67% of peak |
| [latent-diffusion](https://github.com/aghasalim/latent-diffusion-from-scratch) | compression before generation | 5.3x faster training, 6.2x better samples at matched steps |
| [rectified-flow](https://github.com/aghasalim/rectified-flow-from-scratch) | straight paths mean cheap sampling | reflow buys 1-step sampling, 128x less compute, no loss |
| [rlhf-ppo](https://github.com/aghasalim/rlhf-ppo-from-scratch) | optimising a proxy has a cost | gold reward peaks then falls below the starting policy |
| [schrodinger-bridge](https://github.com/aghasalim/schrodinger-bridge-from-scratch) | simulation-free beats alternating | bridge matching 2x to 12x better at a quarter the cost |
| [mla](https://github.com/aghasalim/mla-from-scratch) | the KV cache is the serving wall | 14.2x cache reduction, 120 GB to 8.4 GB at 128k context |
| [world-model](https://github.com/aghasalim/world-model-from-scratch) | learning inside a learned model | the model works, the agent inside it does not, and I say so |
| [vla](https://github.com/aghasalim/vla-from-scratch) | how a policy should emit an action | a regression head averages two valid routes and drives between them |

## How they connect

These are not eight unrelated exercises. Three threads run through them.

**The memory wall.** `flash-attention` attacks it from the kernel side, fusing the
softmax so the score matrix never reaches memory. `mla` attacks the same wall from
the architecture side, compressing the KV cache so there is less to move. Same
problem, different floor of the building.

**Generative paths.** `rectified-flow` uses a straight interpolant,
`latent-diffusion` a curved one, and `schrodinger-bridge` generalises both to
transport between two arbitrary distributions. Flow matching first is deliberate:
it is the simpler object, and diffusion then reads as a special case rather than
as prerequisite machinery. `vla` is where that machinery stops being generative:
the same flow matching objective becomes a robot action head, and the comparison
against a diffusion head is a latency argument rather than a quality one.

**What optimisation costs.** `rlhf-ppo` measures a policy exploiting an imperfect
reward until the true objective collapses. `world-model` measures an agent
learning inside an imperfect model of the world. Both are the same failure in
different clothes: optimising hard against a learned approximation of what you
want.

## The rules every repository follows

1. A reference implementation exists before the optimised one.
2. Never loosen a tolerance to make a test pass.
3. Relative tolerance beats absolute. The bar is "no worse than the naive
   implementation in the same precision", not a magic epsilon.
4. No number that did not come from a measurement. Not from the paper, not
   estimated from the algorithm, not "roughly".
5. Report variance, not just the point estimate. Three seeds minimum for anything
   involving training.
6. Negative results stay in. An ablation table containing only wins is not
   believable.
7. Say "not measured on this hardware" rather than extrapolating.

Rules 6 and 7 do real work. Four of the eight repositories contain a result that
is unflattering to the thing being built, and one contains a claim I made and
then had to withdraw after checking its error bar.

## Things that went wrong, and what they cost

The logbooks are the most useful files in these repositories. A sample:

- A backward drift **reversed twice**, because the DSB target already encodes the
  reversal. Forward loss reached 1.5e11 before I found it.
- A distance metric that compared sorted point clouds elementwise, valid only at
  equal sample sizes. A working run whose output matched the target mean to 0.01
  was scored at 3.04, and I went looking for a transport bug that did not exist.
- A UNet that reconstructed skip channel counts instead of recording them, off by
  one level. GroupNorm caught it; a plain convolution would have accepted the
  wrong shape and trained badly forever.
- A reference policy frozen in place, inherited by every later policy through a
  deepcopy, so the second run of a sweep silently had nothing to optimise.
- A trend read off single-run data **twice**, withdrawn both times once repeats
  gave it an error bar.
- A train/test split that returned fewer objects than a scene needs and left the
  rest at their zero initialised default, quietly putting a training object into
  the held out evaluation set. No error, no crash, caught by a test.

## Author

Aghasalim Mustafazada, third year AI student at Howest, Belgium.
[Website](https://aghasalim.github.io/) ·
[GitHub](https://github.com/aghasalim) ·
[Kaggle](https://www.kaggle.com/aghasalimmustafazada) ·
[ORCID](https://orcid.org/0009-0001-8746-4582)

## License

MIT.
