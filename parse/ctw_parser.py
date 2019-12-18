import networkx as nx


def parse(path):
    f = open(path)
    g = nx.Graph()
    c_vertices = set()

    mode_edges = True
    for line in f:
        entries = line.strip().split(' ')
        if mode_edges:
            if line.lower().strip() == "cvertices":
                mode_edges = False
            else:
                if len(entries) == 2 or (len(entries) == 3 and entries[0].lower() == "e"):
                    try:
                        g.add_edge(int(entries[-2]), int(entries[-1]))
                    except ValueError:
                        pass
        else:
            if len(entries) == 1:
                try:
                    c_vertices.add(int(entries[0]))
                except ValueError:
                    pass
    f.close()

    return g, c_vertices