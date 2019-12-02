class MinDegreeCriterion:
    """Always returns the vertex with lowest degree"""
    def __init__(self, g):
        self.g = g.copy()

        # q is a bucket queue
        self.max_degree = 0
        self.q = [set()]
        for k, v in ((n, len(g[n])) for n in g.nodes):
            if v > self.max_degree:
                for _ in range(0, v - self.max_degree):
                    self.q.append(set())
                self.max_degree = v

            self.q[v].add(k)

        self.cmin = 0

    def choose(self):
        while len(self.q[self.cmin]) == 0:
            self.cmin += 1
            if self.cmin > self.max_degree:
                return None

        # Choose min degree vertex
        return self.q[self.cmin].pop()

    def next(self):
        n = self.choose()

        # Eliminate
        nb = self.g[n]

        # First remove vertex
        self.g.remove_node(n)

        # Decrement degree of neighbors
        for u in nb:
            # Decrement, since degree will decrease after removing n
            self.update_degree(u, -1)

        # Introduce clique among neighbors
        for u, v in ((u, v) for u in nb for v in nb if u > v and u not in self.g[v]):
            self.g.add_edge(u, v)
            self.update_degree(u, 1)
            self.update_degree(v, 1)

        return n

    def update_degree(self, n, inc):
        dgn = len(self.g[n])
        dg = dgn - inc

        if dgn > self.max_degree:
            self.q.append(set())
        if dgn < self.cmin:
            self.cmin = dgn

        self.q[dg].remove(n)
        self.q[dgn].add(n)
