
def ordering_to_decomp(g_in, ordering):
    """Converts an elimination ordering into a decomposition"""

    # TODO: Return full decomp, not only bags
    # ps = {x: ordering.index(x) for x in ordering}
    g = g_in.copy()
    bags = {}
    for n in ordering:
        bags[n] = {n}
        if len(g.nodes) > 1:
            bags[n].update(g[n])
            for u in g[n]:
                for v in g[n]:
                    if u < v:
                        g.add_edge(u, v)
            g.remove_node(n)

    return bags