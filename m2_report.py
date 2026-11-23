# m2_report.py - Milestone M2: the delay-vs-error picture and the results table.
# Run with:  python3 m2_report.py      (after timing_sweep.py and derate.py)
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SERIES = [("trua", "TruA-k (truncation)", "#2a78d6", "o"),
          ("loa",  "LOA-k (lower-part OR)", "#eb6834", "s"),
          ("esa",  "ESA-s (segmentation)", "#1baf7a", "^"),
          ("etaii", "ETAII-k (error-tolerant II)", "#8b5cf6", "D")]     # Day 19
INK, MUTED = "#1b1f27", "#5a6472"

delay = {(r["design"], int(r["k"])): float(r["delay_ps"]) for r in csv.DictReader(open("delay.csv"))}
mse = {(r["design"], int(r["k"])): float(r["MSE"]) for r in csv.DictReader(open("results.csv"))}
picks = list(csv.DictReader(open("picks.csv")))
timer = next(csv.DictReader(open("delay.csv")))["timer"]
d0 = delay[("exact", 0)]

fig, ax = plt.subplots(figsize=(9.5, 5.6))
for fam, label, color, marker in SERIES:
    pts = sorted((delay[(f, k)], mse[(f, k)]) for (f, k) in delay if f == fam and (f, k) in mse)
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=46, marker=marker, color=color,
               edgecolor="white", linewidth=0.8, label=label, zorder=3)

# the timing budgets: an adder must sit LEFT of a line to meet that scenario
lines = [(d0, "accurate adder, fresh")]
for scenario, factor in sorted({(p["scenario"], p["factor"]) for p in picks}, key=lambda t: float(t[1])):
    lines.append((d0 / float(factor), f"budget: {scenario}"))
top = max(mse.values()) * 30
for x, text in lines:
    ax.axvline(x, color=MUTED, linewidth=1, linestyle="--", zorder=1)
    ax.text(x - 4, top, text, rotation=90, va="top", ha="right", fontsize=8.5, color=MUTED)

# label only the chosen designs (each once), with a thin leader line
seen = set()
for p in picks:
    key = (p["design"], int(p["k"]))
    if key in seen:
        continue
    seen.add(key)
    name = {"trua": "TruA", "loa": "LOA", "esa": "ESA", "etaii": "ETAII"}[p["design"]] + "-" + p["k"]
    # TruA labels go above-left, ETAII above-right, the others below-left
    offset, align = {"trua": ((-26, 26), "right"), "etaii": ((22, 22), "left")}.get(p["design"], ((-30, -26), "right"))
    ax.annotate(name, (delay[key], mse[key]), textcoords="offset points",
                xytext=offset, ha=align, fontsize=8.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.7, shrinkB=4))

ax.set_yscale("log")
ax.set_ylim(top=top)
ax.set_xlabel(f"fresh critical-path delay (ps), timer: {timer}", color=INK)
ax.set_ylabel("MSE (log scale), lower is better", color=INK)
ax.set_title("16-bit adders: error vs. delay (left of a dashed line = meets that timing budget)",
             fontsize=10.5, color=INK, loc="left")
ax.grid(True, which="major", color="#e3e6ea", linewidth=0.7, zorder=0)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
ax.tick_params(colors=MUTED)
ax.legend(loc="lower left", frameon=False, fontsize=9)
plt.tight_layout()
plt.savefig("delay_vs_mse.png", dpi=150)
print("saved delay_vs_mse.png")

# ---- m2.md: the table for the Nov 19 update and the slides ----
out = ["# Milestone M2: is truncation the best way to remove a timing guard-band?\n",
       f"Accurate 16-bit ripple-carry adder, fresh: {d0:.1f} ps (timer: {timer}, Nangate 45 nm).\n",
       "Model: slowed delay = fresh delay x factor. A design meets timing if its slowed delay "
       "is at most the fresh accurate delay.\n",
       "| Scenario | Factor | Budget (ps) | Pick | Fresh (ps) | Slowed (ps) | ER % | MRED | MSE | Area (um^2) |",
       "|---|---|---|---|---|---|---|---|---|---|"]
for p in picks:
    name = {"trua": "TruA", "loa": "LOA", "esa": "ESA", "etaii": "ETAII"}[p["design"]] + "-" + p["k"]
    out.append(f"| {p['scenario']} | {p['factor']} | {p['budget_ps']} | {name} | {p['fresh_ps']} | "
               f"{p['slowed_ps']} | {float(p['ER_percent']):.2f} | {float(p['MRED']):.2e} | "
               f"{float(p['MSE']):.4g} | {float(p['area_um2']):.1f} |")
out += ["\n![delay vs MSE](delay_vs_mse.png)\n", "## Verdict\n",
        "(Write two sentences here: is truncation the best choice? Use the numbers above.)\n",
        "## Limitations\n",
        "(Uniform derating, open-source tools, one library, ripple-carry baseline, no power. See the guide.)\n"]
open("m2.md", "w").write("\n".join(out) + "\n")
print("wrote m2.md")
