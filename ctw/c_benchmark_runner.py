import os
import random
import sys

import ctw.solve_ctw as solve_ctw
import parse.ctw_parser as cp
import solve_tw
import tw_utils

#ratios = [0.05, 0.1, 0.2]
ratios = [0.05]
offsets = [0, 1, 2, 3, 4, 5]
input_path = sys.argv[1]
tmp_path = sys.argv[2]
output_path = sys.argv[3]

graph, _ = cp.parse(input_path)

_, instance_name = os.path.split(input_path)
tmp_name = "{}".format(os.getpid())
inpf = os.path.join(tmp_path, tmp_name +".in")
outpf = os.path.join(tmp_path, tmp_name +".out")


def output_graph(b, t, f):
    with open(f, "w+") as decomp_file:
        for u, v in t.edges:
            decomp_file.write("{} {}\n".format(u, v))
        decomp_file.write("\n")
        for k, bag in b.items():
            decomp_file.write("b {} {}\n".format(k, " ".join(str(x) for x in bag)))


base_tw, base_ord = solve_tw.solve(graph, inpf, outpf)

# Could not solve tw, just abort
if base_tw is None:
    exit(1)

base_decomp = tw_utils.ordering_to_decomp(graph, base_ord)
output_graph(base_decomp[0], base_decomp[1], os.path.join(output_path, instance_name+".tw.decomp"))

# Fix seed for reproducibility
random.seed(a=str(len(graph.edges) + len(graph.nodes)))

# shuffle vertices randomly
vertex_list = list(graph.nodes)
vertex_list.sort()
for i in range(0, len(vertex_list)-1):
    nxt = random.randint(i, len(vertex_list) - 1)
    vertex_list[i], vertex_list[nxt] = vertex_list[nxt], vertex_list[i]


for ratio in ratios:
    c_output_name = "{}.{}".format(instance_name, "%.2f" % ratio)[1:]
    with open(os.path.join(output_path, "{}.result".format(c_output_name)), "w+") as c_output:
        # Establish values for base decomposition
        c_vertices = set(vertex_list[x] for x in range(0, int(ratio * len(vertex_list)) + 1))
        base_c = max(len(x & c_vertices) for x in base_decomp[0].values())
        c_output.write("t w {} c {}\n".format(base_tw, base_c))

        min_c, max_t, c_ord = solve_ctw.solve_c(graph, c_vertices, inpf, outpf)

        for offset in offsets:
            c_tw, c_ord = solve_ctw.solve(graph, c_vertices, inpf, outpf, c_val=min_c + offset, tub=max_t+1)

            if c_tw is not None:
                c_decomp = tw_utils.ordering_to_decomp(graph, c_ord)
                c_c = max(len(x & c_vertices) for x in c_decomp[0].values())
                c_output.write("{} w {} c {}\n".format(offset, c_tw, c_c))
                output_graph(c_decomp[0], c_decomp[1], os.path.join(output_path, c_output_name + ".decomp"))

                # Already optimal
                max_t = c_tw
                if c_tw == base_tw:
                    break
