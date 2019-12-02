import sys
import networkx as nx
import sv_improved as svi
from ctw import c_sv as svc
import upper_bounds as ubs
import lower_bounds as lbs
import subprocess
import os

f = open(sys.argv[1])
g = nx.Graph()
c_vertices = set()

mode_edges = True
for line in f:
    entries = line.strip().split(' ')
    if mode_edges:
        if line.lower().strip() == "cvertices":
            mode_edges = False
        else:
            if len(entries) == 2:
                try:
                    g.add_edge(int(entries[0]), int(entries[1]))
                except ValueError:
                    pass
    else:
        if len(entries) == 1:
            try:
                c_vertices.add(int(entries[0]))
            except ValueError:
                pass
f.close()

print(f"Found {len(g.nodes)} nodes and {len(g.edges)} edges")

ub = ubs.greedy_min_degree(g)
print(f"Upper Bound: {ub}")

lb = lbs.lbnp(g)
print(f"Lower Bound: {lb}")


cval = ub - 1

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
    p1.wait(750)

    if p1.returncode == 10:
        print("Success")
        ub = cval
        cval -= 1
    else:
        print("Failed")
        lb = cval
        cval += 1

    f2.close()
    os.remove(filename)

print(f"\n\nFound tw {cval}")



