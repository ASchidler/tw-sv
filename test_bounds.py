import os
import parse.ctw_parser as ps
import ctw.c_upper_bound as cb
import ctw.c_lower_bound as lb
from sys import maxsize

path = "/home/aschidler/tmp/ctree/"
results = {}

for r, d, f in os.walk(path):
    for file in sorted(f):
        g, c_vertices = ps.parse(os.path.join(r, file))

        if len(c_vertices) == 0:
            print(f"Not a ctree instance {file}")

        print(file)
        print(f"Lower Bound: {lb.c_lower_bound(g, c_vertices)}")
        bounds = {
            "min_degree": cb.min_degree(g, c_vertices),
            "min_degree_c": cb.min_degree_min_c(g, c_vertices),
            "min_c": cb.min_c(g, c_vertices),
            "two_pass": cb.twopass(g, c_vertices),
            "incremental": cb.incremental_c_min_degree(g, c_vertices),
            "c_bound": cb.c_bound_min_degree(g, c_vertices, 3)
        }

        for k, v in bounds.items():
            if k not in results:
                results[k] = [0, 0, 0, 0]

            print(f"{k}: {v}")

            if v[0] != maxsize:
                results[k][0] += v[0]
                results[k][1] += v[1]
                results[k][2] += 1


for k, v in results.items():
    print(f"{k}: {v[0]*1.0/v[2]}\t\t{v[1]*1.0/v[2]}")
