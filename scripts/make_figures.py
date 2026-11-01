"""Figures in docs/ for the README.

claims.png: the headline values, read from verify/claims.tsv (no other numbers).
contact-sheet.png: one existing result image from each sibling repository, which
must be cloned next to this one (../<repo>). Pass another parent dir as argv[1].
"""
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
OUT.mkdir(exist_ok=True)
SIBLINGS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent

c = {r["id"]: r for r in csv.DictReader((ROOT / "verify" / "claims.tsv").open(), delimiter="\t")}
a = lambda k: float(c[k]["a"])
pub = lambda k: float(c[k]["published"])
GREY, BLUE, RED = "#9aa0a6", "#2f6fdf", "#d0453a"


def bars(ax, labels, vals, colors, fmt, title, ylabel, log=False):
    ax.bar(labels, vals, color=colors, width=0.6)
    for i, v in enumerate(vals):
        ax.annotate(fmt(v), (i, v), ha="center", va="bottom" if v >= 0 else "top",
                    xytext=(0, 3 if v >= 0 else -3), textcoords="offset points", fontsize=9)
    if log:
        ax.set_yscale("log")
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=8)
    ax.tick_params(labelsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.margins(y=0.25)


fig, axs = plt.subplots(2, 4, figsize=(13, 6))
axs = axs.ravel()
bars(axs[0], ["unfused", "fused"], [a("fa_before"), a("fa_after")], [GREY, BLUE],
     lambda v: f"{v:g}%", "flash-attention", "throughput, % of fp32 peak")
bars(axs[1], ["training\nspeed", "sample\nquality"], [pub("ld_speed"), pub("ld_quality")], [BLUE, BLUE],
     lambda v: f"{v:g}x", "latent-diffusion", "better than pixel baseline (x)")
axs[1].axhline(1, color=GREY, lw=1, ls="--")
bars(axs[2], ["before\nreflow", "after\nreflow"], [pub("rf_steps"), 1], [GREY, BLUE],
     lambda v: f"{v:g} NFE", "rectified-flow", "sampling steps (NFE)", log=True)
bars(axs[3], ["smallest\ngap", "largest\ngap"], [pub("sb_lo"), pub("sb_hi")], [BLUE, BLUE],
     lambda v: f"{v:g}x", "schrodinger-bridge", "bridge matching: sliced W2\nlower than DSB (x)")
axs[3].axhline(1, color=GREY, lw=1, ls="--")
bars(axs[4], ["full KV", "MLA latent"], [a("mla_before"), float(c["mla_ratio"]["b"])],
     [GREY, BLUE], lambda v: f"{v:g} GB", "mla", "KV cache at 128k context (GB)")
bars(axs[5], ["starting\npolicy", "peak", "end of\ntraining"], [a("rlhf_ref"), a("rlhf_peak"), a("rlhf_end")],
     [GREY, BLUE, RED], lambda v: f"{v:+.2f}", "rlhf-ppo", "gold reward")
axs[5].axhline(0, color="k", lw=0.6)
bars(axs[6], ["regression\nhead", "flow\nhead"], [a("vla_reg"), a("vla_flow")], [RED, BLUE],
     lambda v: f"{v:g}", "vla", "collisions per episode")
ax = axs[7]
ax.axis("off")
ax.set_title("world-model", fontsize=10, fontweight="bold")
ax.text(0.5, 0.5, f"negative result:\nat {a('wm_short'):,.0f} env steps\nthe agent inside the\nlearned model does not\nbeat a random policy",
        ha="center", va="center", fontsize=10, transform=ax.transAxes,
        bbox=dict(boxstyle="round", fc="#f3f3f3", ec=GREY))
fig.suptitle("Headline results, as listed in verify/claims.tsv (all on a laptop CPU)", fontsize=12)
fig.tight_layout()
fig.savefig(OUT / "claims.png", dpi=150)
plt.close(fig)

# one existing result image per repository, the one each README leads its results with
SHEET = [
    ("flash-attention-from-scratch", "results/fusion.png"),
    ("latent-diffusion-from-scratch", "results/quality-vs-cost.png"),
    ("rectified-flow-from-scratch", "results/nfe-quality.png"),
    ("rlhf-ppo-from-scratch", "results/overoptimization.png"),
    ("schrodinger-bridge-from-scratch", "results/methods.png"),
    ("mla-from-scratch", "results/cache.png"),
    ("world-model-from-scratch", "results/open-loop.png"),
    ("vla-from-scratch", "results/multimodality.png"),
]
fig, axs = plt.subplots(4, 2, figsize=(16, 15))
for ax, (repo, rel) in zip(axs.ravel(), SHEET):
    im = Image.open(SIBLINGS / repo / rel).convert("RGB")
    im.thumbnail((1200, 1200))
    ax.imshow(im)
    ax.set_title(f"{repo}  ({rel})", fontsize=12, fontweight="bold")
    ax.axis("off")
fig.tight_layout(h_pad=1.5)
fig.savefig(OUT / "contact-sheet.png", dpi=150)
plt.close(fig)
# keep the PNG small enough for a README
Image.open(OUT / "contact-sheet.png").convert("RGB").quantize(256).save(OUT / "contact-sheet.png", optimize=True)
print("figures written")
