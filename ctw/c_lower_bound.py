import lower_bounds as lb
import networkx as nx


def c_lower_bound(g, reds):
    """This lower bound is based on calculating the normal lower bound for the subgraph induced by the reds"""

    if len(reds) == 0:
        return 0

    # Find connected subgraphs
    to_find = set(reds)
    q = []
    ng = None
    bound = 1

    while True:
        if not q:
            # Compute lb
            if ng is not None and len(ng.nodes) > 1:
                # Do not use LBN, as the lemma is not proven for CTW and produces wrong results
                bound = max(bound, lb.mmd(ng) + 1)

            if not to_find:
                break

            q.append(to_find.pop())
            ng = nx.Graph()

        n = q.pop()
        for u in g[n]:
            if u in reds:
                ng.add_edge(n, u)
            if u in to_find:
                to_find.remove(u)
                q.append(u)

    return bound

def c_lower_bound(g, reds):
    """This lower bound is based on calculating the normal lower bound for the subgraph induced by the reds"""

    if len(reds) == 0:
        return 0

    # Find connected subgraphs
    to_find = set(reds)
    q = []
    ng = None
    bound = 1

    while True:
        if not q:
            # Compute lb
            if ng is not None and len(ng.nodes) > 1:
                # Do not use LBN, as the lemma is not proven for CTW and produces wrong results
                bound = max(bound, lb.mmd(ng) + 1)

            if not to_find:
                break

            q.append(to_find.pop())
            ng = nx.Graph()

        n = q.pop()
        for u in g[n]:
            if u in reds:
                ng.add_edge(n, u)
            if u in to_find:
                to_find.remove(u)
                q.append(u)

    return bound