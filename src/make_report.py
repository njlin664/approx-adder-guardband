# make_report.py - builds results.md: your numbers next to the paper's table rows.
# Run with:  python3 src/make_report.py
import csv

# Paper values: (ER %, MRED in units of 1e-3, MSE) and which table they came from.
PAPER = {
    ("trua", 2):  (93.74, 0.06, 1.15e1, "Table III"),
    ("trua", 5):  (99.90, 0.70, 1.13e3, "Table II"),
    ("trua", 9):  (99.99, 10.70, 3.04e5, "Table IV"),
    ("loa", 3):   (57.80, 0.03, 4.00, "Table III"),
    ("loa", 6):   (82.21, 0.25, 2.56e2, "Table II"),
    ("loa", 10):  (94.36, 4.00, 6.55e4, "Table IV"),
    ("esa", 8):   (49.83, 2.70, 3.26e4, "Table II"),
}

mine = {}
for r in csv.DictReader(open("data/results.csv")):
    mine[(r["design"], int(r["k"]))] = r

lines = []
lines.append("# Error metrics: my results vs. the paper\n")
lines.append("My numbers: exhaustive simulation of all 2^32 input pairs. MRED skips the single case a = b = 0.\n")
lines.append("| Design | ER % (mine) | ER % (paper) | MRED x1e-3 (mine) | "
             "MRED x1e-3 (paper) | MSE (mine) | MSE (paper) | MSE mine/paper | Paper table |")
lines.append("|---|---|---|---|---|---|---|---|---|")
for (d, k), (er_p, mred_p, mse_p, tab) in PAPER.items():
    r = mine[(d, k)]
    er, mred, mse = float(r["ER_percent"]), float(r["MRED"]) * 1e3, float(r["MSE"])
    lines.append(f"| {d.upper()}-{k} | {er:.2f} | {er_p:.2f} | {mred:.3f} | {mred_p:.2f} | "
                 f"{mse:.4g} | {mse_p:.4g} | {mse/mse_p:.3f} | {tab} |")

lines.append("\n## All designs I simulated\n")
lines.append("| Design | ER % | MED | NMED | MRED | MSE |")
lines.append("|---|---|---|---|---|---|")
for (d, k), r in mine.items():
    lines.append(f"| {d.upper()}-{k} | {float(r['ER_percent']):.2f} | {float(r['MED']):.4g} | "
                 f"{float(r['NMED']):.3e} | {float(r['MRED']):.3e} | {float(r['MSE']):.4g} |")

lines.append("\n## Where my numbers differ from the paper, and why\n")
lines.append("(Write one paragraph here. See the guide for what to say.)\n")

open("reports/results.md", "w").write("\n".join(lines) + "\n")
print("\n".join(lines[:12]))
print("\nwrote results.md")
