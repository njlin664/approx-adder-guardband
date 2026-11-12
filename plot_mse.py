# plot_mse.py - draws mse_vs_k.png from results.csv and prints the TruA/LOA ratio table.
# Run with:  python3 plot_mse.py
import csv
import matplotlib
matplotlib.use("Agg")            # draw to a file, no window needed
import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("results.csv")))

def series(design):
    pts = [(int(r["k"]), float(r["MSE"])) for r in rows if r["design"] == design]
    return sorted(pts)

trua, loa, esa = series("trua"), series("loa"), series("esa")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.semilogy([p[0] for p in trua], [p[1] for p in trua], "o-", label="TruA-k (truncation)")
ax1.semilogy([p[0] for p in loa], [p[1] for p in loa], "s-", label="LOA-k (lower-part OR)")
ax1.set_xlabel("k (number of low bits approximated)")
ax1.set_ylabel("MSE (log scale)")
ax1.set_title("Truncation vs. LOA, 16-bit adder")
ax1.grid(True, which="both", alpha=0.3)
ax1.legend()

ax2.semilogy([p[0] for p in esa], [p[1] for p in esa], "^-", color="tab:green")
ax2.set_xlabel("segment size s (bits)")
ax2.set_ylabel("MSE (log scale)")
ax2.set_title("ESA-s (equal segmentation)")
ax2.grid(True, which="both", alpha=0.3)

plt.tight_layout()
plt.savefig("mse_vs_k.png", dpi=150)
print("saved mse_vs_k.png\n")

# TruA-(k-1) and LOA-k leave the same number of bits in the exact carry chain.
t = dict(trua)
l = dict(loa)
print(" k   TruA-(k-1) MSE    LOA-k MSE     ratio")
for k in range(2, 13):
    print(f"{k:2d}   {t[k-1]:12.4g}   {l[k]:12.4g}   {t[k-1]/l[k]:6.2f}x")
