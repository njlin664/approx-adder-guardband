# timing_sweep.py - synthesize every adder and measure its critical-path delay.
# Run with:  python3 timing_sweep.py        (about a minute)
# Writes delay.csv. Uses OpenSTA if it is installed; ABC's own estimate otherwise.
import csv, os, re, shutil, subprocess, sys

LIB = "NangateOpenCellLibrary_typical.lib"
OUT = "build"                                   # netlists and logs go here

# (family, k, Verilog module, parameter name)
DESIGNS  = [("exact", 0, "adder_exact", None), ("behav", 0, "adder_behav", None)]
DESIGNS += [("trua", k, "adder_trua", "K") for k in range(1, 13)]
DESIGNS += [("loa",  k, "adder_loa",  "K") for k in range(1, 13)]
DESIGNS += [("esa",  s, "adder_esa",  "S") for s in range(2, 9)]

# The exact mapping recipe ABC runs, so every design is treated the same way.
ABC_SCRIPT = """strash
&get -n
&fraig -x
&put
scorr
dc2
dretime
strash
&get -n
&dch -f
&nf
&put
topo
stime -p
"""

def find_sta():
    """Return the OpenSTA program, or None if it is not installed."""
    for candidate in [shutil.which("sta"), os.path.expanduser("~/OpenSTA/build/sta")]:
        if candidate and os.path.exists(candidate):
            return candidate
    return None

def synthesize(family, k, module, param):
    """Run Yosys. Returns (netlist file, cell count, area in um^2, ABC delay in ps)."""
    tag = f"{family}_{k}"
    netlist, log = f"{OUT}/{tag}.v", f"{OUT}/{tag}.synth.log"
    chparam = f" -chparam {param} {k}" if param else ""
    script = f"""read_verilog adders.v
hierarchy -top {module}{chparam}
synth -top {module} -flatten
abc -liberty {LIB} -script {OUT}/abc_map.script
opt_clean
delete t:$scopeinfo
stat -liberty {LIB}
write_verilog -noattr {netlist}
"""
    open(f"{OUT}/{tag}.ys", "w").write(script)
    subprocess.run(["yosys", "-q", "-l", log, f"{OUT}/{tag}.ys"], check=True,
                   stdout=subprocess.DEVNULL)
    text = open(log).read()
    cells = int(re.findall(r"Number of cells:\s+(\d+)", text)[-1])
    area = float(re.findall(r"Chip area for module.*?:\s+([\d.]+)", text)[-1])
    abc_ps = float(re.findall(r"Delay =\s*([\d.]+) ps", text)[-1])
    return netlist, cells, area, abc_ps

def run_sta(sta, family, k, module, netlist):
    """Run OpenSTA on one netlist. Returns the critical-path delay in ps."""
    tag = f"{family}_{k}"
    script = f"""read_liberty {LIB}
read_verilog {netlist}
link_design {module}
create_clock -name vclk -period 10
set_input_delay 0 -clock vclk [all_inputs]
set_output_delay 0 -clock vclk [all_outputs]
set_driving_cell -lib_cell BUF_X1 [all_inputs]
set_load 3.0 [all_outputs]
report_checks -path_delay max -digits 4
"""
    open(f"{OUT}/{tag}.sta.tcl", "w").write(script)
    result = subprocess.run([sta, "-no_init", "-no_splash", "-exit", f"{OUT}/{tag}.sta.tcl"],
                            capture_output=True, text=True)
    open(f"{OUT}/{tag}.sta.log", "w").write(result.stdout + result.stderr)
    arrival_ns = float(re.findall(r"([\d.]+)\s+data arrival time", result.stdout)[0])
    return arrival_ns * 1000.0                   # the library's time unit is ns

if not os.path.exists(LIB):
    sys.exit(f"ERROR: {LIB} is not in this folder. See Day 9 of the guide.")
os.makedirs(OUT, exist_ok=True)
open(f"{OUT}/abc_map.script", "w").write(ABC_SCRIPT)

sta = find_sta()
print("timer:", f"OpenSTA ({sta})" if sta else "ABC estimate only (OpenSTA not found)")

rows = []
for family, k, module, param in DESIGNS:
    netlist, cells, area, abc_ps = synthesize(family, k, module, param)
    sta_ps = run_sta(sta, family, k, module, netlist) if sta else None
    delay = sta_ps if sta_ps is not None else abc_ps
    rows.append([family, k, cells, f"{area:.3f}", f"{abc_ps:.1f}",
                 f"{sta_ps:.1f}" if sta_ps is not None else "", f"{delay:.1f}",
                 "opensta" if sta_ps is not None else "abc"])
    print(f"{family:>5} {k:2d}   cells {cells:3d}   area {area:7.2f}   delay {delay:7.1f} ps")

with open("delay.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["design", "k", "cells", "area_um2", "abc_delay_ps", "sta_delay_ps",
                "delay_ps", "timer"])
    w.writerows(rows)
print("wrote delay.csv")
