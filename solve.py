import sys
import networkx as nx
from twsolver import GraphSatTw
import sv
import sv_improved as svi
import bounds

f = open(sys.argv[1])
g = nx.Graph()

for line in f:
    entries = line.strip().split(' ')
    if len(entries) == 2:
        try:
            g.add_edge(int(entries[0]), int(entries[1]))
        except ValueError:
            pass
f.close()

# changed = True
# while changed:
#     changed = False
#     for n in g.nodes:
#         if len(g[n]) == 1:
#             g.remove_node(n)
#             changed = True
#             break
#         if len(g[n]) == 2:
#             nbs = list(g[n])
#             g.add_edge(nbs[0], nbs[1])
#             g.remove_node(n)
#             changed = True
#             break

print(f"Found {len(g.nodes)} nodes and {len(g.edges)} edges")

ub = bounds.greedy(g)
print(f"Upper Bound: {ub}")

lb = bounds.lbnp(g)
print(f"Lower Bound: {lb}")



f2 = open("test.txt", "w+")
#slv = GraphSatTw(g, stream=f2)
#slv.encode()
slv = svi.ImprovedSvEncoding(f2, g)
#slv.encode_smt(g, f2, lb=lb, ub=ub)
slv.encode_sat(ub-3)

f2.close()

