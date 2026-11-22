	# compare_modes.py - Day 15(c): ripple (area mode) vs fast (speed mode) delay for every k.
# Run with:  python3 compare_modes.py      (needs delay.csv and delay_fast.csv)
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def load(path):
    return {(r["design"], int(r["k"])): float(r["delay_ps"]) for r in csv.DictReader(open(path))}

ripple, fast = load("delay.csv"), load("delay_fast.csv")
ks = range(1, 13)
fig, ax = plt.subplots(figsize=(8, 4.6))
for d, mode, color in [(ripple, "ripple (area mode)", "#2a78d6"), (fast, "fast (speed mode)", "#eb6834")]:
    ax.plot(ks, [d[("trua", k)] for k in ks], marker="o", color=color, label=f"TruA-k, {mode}")
    ax.plot(ks, [d[("loa", k)] for k in ks], marker="s", color=color, linestyle="--",
            label=f"LOA-k, {mode}")
    exact = d[("exact", 0)]
    ax.axhline(exact, color=color, linewidth=0.8, linestyle=":")
    ax.text(12.2, exact, f"exact {exact:.0f} ps", color=color, fontsize=8, va="center")
ax.set_xlabel("k (low bits approximated)")
ax.set_ylabel("critical-path delay (ps)")
ax.set_title("Cutting bits helps a ripple adder a lot, a fast adder much less",
             loc="left", fontsize=10.5)
ax.set_xlim(0.5, 14.2)
ax.grid(True, alpha=0.3)
ax.legend(frameon=False, fontsize=8, loc="lower left")
plt.tight_layout()
plt.savefig("compare_modes.png", dpi=150)
print("saved compare_modes.png")

for mode, d in [("ripple", ripple), ("fast", fast)]:
    e, t6, t9 = d[("exact", 0)], d[("trua", 6)], d[("trua", 9)]
    print(f"{mode:>6}: exact {e:.1f} ps, TruA-6 {t6:.1f} ps ({100 * (1 - t6 / e):.0f}% faster), "
          f"TruA-9 {t9:.1f} ps ({100 * (1 - t9 / e):.0f}% faster)")
