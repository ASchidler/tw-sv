import os
import random
import sys

import ctw.c_lower_bound as lb
import ctw.c_upper_bound as cb
import ctw.ctw_parser as cp

ratios = [0.05, 0.1, 0.2]
input_path = sys.argv[1]
output_path = sys.argv[2]
graph, _ = cp.parse(input_path)
# Fix seed for reproducibility
random.seed(a=str(len(graph.edges) + len(graph.nodes)))

_, instance_name = os.path.split(input_path)

# shuffle vertices randomly
vertex_list = list(graph.nodes)
vertex_list.sort()
for i in range(0, len(vertex_list)-1):
    nxt = random.randint(i, len(vertex_list) - 1)
    vertex_list[i], vertex_list[nxt] = vertex_list[nxt], vertex_list[i]


for ratio in ratios:
    instance_name = instance_name.replace(".bz2", "")
    c_output_name = "{}{}".format(instance_name, ("%.2f" % ratio)[1:])
    c_vertices = set(vertex_list[x] for x in range(0, int(ratio * len(vertex_list)) + 1))
    lb_c = lb.c_lower_bound(graph, c_vertices)

    bounds = {
        "min_degree": cb.min_degree(graph, c_vertices),
        "min_degree_c": cb.min_degree_min_c(graph, c_vertices),
        "min_c": cb.min_c(graph, c_vertices),
        "two_pass": cb.twopass(graph, c_vertices),
        "incremental": cb.incremental_c_min_degree(graph, c_vertices, lb_c),
        "c_bound": cb.c_bound_min_degree(graph, c_vertices, lb_c + 1)
    }

    min_w = min(x[0] for x in bounds.values())
    min_c = min(x[1] for x in bounds.values())

    # Output results
    with open(os.path.join(output_path, "{}.heuristic".format(c_output_name)), "w+") as c_output:
        c_output = sys.stdout
        c_output.write(f"{min_w};{min_c}")
        heuristics = list(bounds.keys())
        heuristics.sort()
        for h in heuristics:
            c_output.write(f";{bounds[h][0]};{bounds[h][1]}")
        c_output.write(os.linesep)
