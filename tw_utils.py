import networkx as nx
from networkx import DiGraph


def ordering_to_decomp(g_in, ordering):
    """Converts an elimination ordering into a decomposition, returns bag, tree and the tree's root"""

    bags = {n: {n} for n in ordering}
    tree = DiGraph()
    ps = {x: ordering.index(x) for x in ordering}

    # Add edges to bags
    for u, v in g_in.edges:
        if ps[v] < ps[u]:
            u, v = v, u
        bags[u].add(v)

    for n in ordering:
        A = set(bags[n])
        if len(A) > 1:
            A.remove(n)
            _, nxt = min((ps[x], x) for x in A)

            bags[nxt].update(A)
            tree.add_edge(nxt, n)

    return bags, tree, ordering[len(ordering) - 1]


def clean_tree(bags, tree, root):
    """Cleans the tree by removing subsumed bags, i.e. the resulting decomposition will be equal but smaller"""
    import queue as qu
    # Remove subsumed bags
    q = qu.Queue()
    q.put(root)

    while not q.empty():
        n = q.get()

        nbs = set(tree.successors(n))
        nbs.update(tree.predecessors(n))
        target = None

        for u in nbs:
            if bags[u].issubset(bags[n]) or bags[u].issuperset(bags[n]):
                target = u
                break

        if target is None:
            for u in tree.successors(n):
                q.put(u)

        else:
            q.put(target)
            for u in tree.successors(n):
                if u != target:
                    tree.add_edge(target, u)
            for u in tree.predecessors(n):
                if u != target:
                    tree.add_edge(u, target)

            bags[target] = bags[target] if len(bags[target]) >= len(bags[n]) else bags[n]
            bags.pop(n)
            tree.remove_node(n)

    return tree, bags


def verify_decomposition(g_in, bags, tree):
    if not nx.is_tree(tree):
        print("Not a tree")
        return False

    # Assuming a connected graph, it suffices to check every edge
    for u, v in g_in.edges():
        found = False
        for _, b in bags.items():
            if u in b and v in b:
                found = True
                break

        # Edge not covered
        if not found:
            print(f"Edge {u}, {v} not covered")
            return False

    # Check connectedness
    for u in g_in.nodes():
        ns = set(k for k, v in bags.items() if u in v)

        # For some reason weak connectedness does not work in networkx...
        found = set()
        q = [next(ns.__iter__())]

        while q:
            n = q.pop()
            found.add(n)
            nbs = set(tree.predecessors(n))
            nbs.update(tree.successors(n))
            q.extend((nbs & ns) - found)

        if found != ns:
            print(f"{u} does not induce a connected component")
            return False

    return True