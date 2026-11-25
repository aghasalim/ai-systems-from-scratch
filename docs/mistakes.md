# Things that went wrong, and what they cost

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
