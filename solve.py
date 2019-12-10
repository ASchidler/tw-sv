import sys
import sv_improved as svi
from ctw import c_sv as svc
import upper_bounds as ubs
import lower_bounds as lbs
import subprocess
import os
import ctw.c_bound as cb
import parse.ctw_parser as ps

g, c_vertices = ps.parse(sys.argv[1])

print(f"Found {len(g.nodes)} nodes and {len(g.edges)} edges")

if len(c_vertices) == 0:
    ub = ubs.greedy_min_degree(g)
    print(f"Upper Bound: {ub}")

    lb = lbs.lbnp(g)
    print(f"Lower Bound: {lb}")
else:
    bounds = {
        "min_degree": cb.min_degree(g, c_vertices),
        "min_degree_c": cb.min_degree_min_c(g, c_vertices),
        "min_c": cb.min_c(g, c_vertices),
        "two_pass": cb.twopass(g, c_vertices),
        "incremental": cb.incremental_c_min_degree(g, c_vertices),
        "c_bound": cb.c_bound_min_degree(g, c_vertices, 3),
    }

    for k, v in bounds.items():
        print(f"{k}: {v}")

    ub = min(bounds.values())[0]
    print(f"Upper Bound: {ub}")

    lb = lbs.lbnp(g)
    print(f"Lower Bound: {lb}")


cval = ub - 1
lb_done = False

# Upper bound is already a solution, so look starting from ub - 1
filename = f"{os.getpid()}_encoding.txt"
while lb <= cval < ub:
    print(f"\nRunning {cval}")
    f2 = open(filename, "w+")

    if len(c_vertices) == 0:
        slv = svi.ImprovedSvEncoding(f2, g)
    else:
        slv = svc.CTwEncoding(c_vertices, 2, f2, g)

    slv.encode_sat(cval)
    f2.seek(0)
    p1 = subprocess.Popen(['minisat', '-verb=0'], stdin=f2)
    try:
        p1.wait(300)

        if p1.returncode == 10:
            print("Success")
            ub = cval
            cval -= 1
        else:
            print("Failed")
            cval += 1
            lb = cval

    except subprocess.TimeoutExpired:
        # If Timeout exceeded, try other direction
        if not lb_done:
            print("Timeout, trying other direction")
            lb_done = True
            cval = lb
        else:
            print(f"Solving timed out, width is between {lb} and {ub}")
            exit(1)

    f2.close()
    os.remove(filename)

print(f"\n\nFound tw {cval}")



