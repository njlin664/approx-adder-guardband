# derate.py - which adders still meet timing after aging or heat slow the chip down?
# Run with:  python3 src/derate.py          (uses delay.csv,      writes picks.csv)
#            python3 src/derate.py fast     (uses delay_fast.csv, writes picks_fast.csv; Day 15)
# Model: slowed delay = fresh delay x factor. Goal: slowed approximate adder must be
# no slower than the FRESH accurate adder, so no extra clock margin is needed.
import csv, sys

FAST = len(sys.argv) > 1 and sys.argv[1] == "fast"
DELAY_CSV = "data/delay_fast.csv" if FAST else "data/delay.csv"
PICKS_CSV = "data/picks_fast.csv" if FAST else "data/picks.csv"

# Slowdown factors taken from the paper's accurate 16-bit adder:
#   Table II: 138.6 ps fresh -> 149.5 ps after 10 years   (x1.08)
#   Table IV: 143.5 ps at 25 C -> 196.7 ps at 70 C        (x1.37)
SCENARIOS = [("aging, 10 years", 1.08), ("temperature, 70 C", 1.37)]
FAMILIES = [("trua", "TruA"), ("loa", "LOA"), ("esa", "ESA"), ("etaii", "ETAII")]

delay, area = {}, {}
for r in csv.DictReader(open(DELAY_CSV)):
    key = (r["design"], int(r["k"]))
    delay[key] = float(r["delay_ps"])
    area[key] = float(r["area_um2"])

err = {}
for r in csv.DictReader(open("data/results.csv")):
    err[(r["design"], int(r["k"]))] = r

d0 = delay[("exact", 0)]
kind = "fast, speed mode" if FAST else "ripple-carry"
print(f"fresh accurate adder ({kind}): {d0:.1f} ps, area {area[('exact', 0)]:.1f} um^2\n")

picks = []
for name, factor in SCENARIOS:
    budget = d0 / factor
    print(f"=== {name}: everything runs {factor:.2f}x slower ===")
    print(f"an adder meets timing if its fresh delay is at most {d0:.1f} / {factor:.2f} = {budget:.1f} ps")
    print(f"{'pick':<8}{'fresh ps':>9}{'slowed ps':>10}{'ER %':>8}{'MRED':>11}{'MSE':>11}{'area':>8}")
    for fam, label in FAMILIES:
        if not any(f == fam for (f, _) in err):
            continue                                   # no error metrics for this family yet
        ok = [k for (f, k) in delay if f == fam and delay[(f, k)] <= budget and (f, k) in err]
        if not ok:
            print(f"{label:<8} no setting meets timing")
            continue
        k = min(ok, key=lambda kk: float(err[(fam, kk)]["MSE"]))     # least error that still fits
        e = err[(fam, k)]
        d = delay[(fam, k)]
        print(f"{label + '-' + str(k):<8}{d:>9.1f}{d * factor:>10.1f}{float(e['ER_percent']):>8.2f}"
              f"{float(e['MRED']):>11.2e}{float(e['MSE']):>11.4g}{area[(fam, k)]:>8.1f}")
        picks.append([name, factor, f"{budget:.1f}", fam, k, f"{d:.1f}", f"{d * factor:.1f}",
                      e["ER_percent"], e["MRED"], e["MSE"], f"{area[(fam, k)]:.3f}"])
    print()

with open(PICKS_CSV, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["scenario", "factor", "budget_ps", "design", "k", "fresh_ps", "slowed_ps",
                "ER_percent", "MRED", "MSE", "area_um2"])
    w.writerows(picks)
print("wrote", PICKS_CSV)
