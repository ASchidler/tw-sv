import networkx as nx
from random import randint
import os


def generate_random(vertices, path, delete_edges, c_vertices):
    g = nx.Graph()

    # Create full graph
    for i in range(1, vertices + 1):
        for j in range(i + 1, vertices + 1):
            g.add_edge(i, j)

    # Remove random edges
    for _ in range(0, int(vertices * (vertices + 1) / 2 * delete_edges)):
        # Do not disconnect graph
        candidates = [x for x in g.nodes if len(g[x]) > 1]
        u = candidates[randint(0, len(candidates) - 1)]
        while all(len(g[v]) == 1 for v in g[u]):
            u = candidates[randint(0, len(candidates) - 1)]

        # Select second node for edge, again do not disconnect
        nb = list(x for x in g[u] if len(g[x]) > 1)
        v = nb[randint(0, len(nb) - 1)]

        g.remove_edge(u, v)

    # Select c vertices randomly
    c_v = set()
    while len(c_v) < vertices * c_vertices:
        c_v.add(randint(1, vertices - 1))

    # Write instance
    f = open(path, "w+")
    f.write(f"p tw {vertices} {len(g.edges)}\n")
    for u, v in g.edges:
        f.write(f"{u} {v}\n")

    f.write("\nCVertices\n")
    for u in c_v:
        f.write(f"{u}\n")

p = "/home/aschidler/tmp/ctree"
for i in range(21, 31):
    generate_random(150, os.path.join(p, f"{i}.gr"), 0.8, 0.1)
