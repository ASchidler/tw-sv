import sv
import networkx.algorithms.clique as cq1
import networkx.algorithms.approximation.clique as cq2


class ImprovedSvEncoding(sv.SvEncoding):
    """Improvements upon the Samer-Veith encoding"""
    def encode(self):
        # Add clique literals first, allows solver to immediately discard later redundant clauses
        self.encode_cliques()

        # These are binary clauses that are not necessary, but help the solver
        for i in range(0, len(self.g.nodes)):
            for j in range(i+1, len(self.g.nodes)):
                # Arcs cannot go in both directions
                self._add_clause(-self.arc[j][i], -self.arc[i][j])
                # Enforce arc direction from smaller to bigger ordered vertex
                self._add_clause(-self.ord[i][j], -self.arc[j][i])
                self._add_clause(self.ord[i][j], -self.arc[i][j])

        super().encode()

    def encode_cliques(self):
        """Enforces lexicographical ordering of the cliques"""

        # This is probably slow at some point... Change to approx based on some heuristic?
        _, clique = max((len(c), c) for c in cq1.find_cliques(self.g))
        # clique = cq2.max_clique(self.g)

        # Put clique at the end of the ordering
        for n in self.g.nodes:
            if n in clique:
                continue

            n = self.node_lookup[n]
            for u in clique:
                u = self.node_lookup[u]
                self._add_clause(self._ord(n, u))

        # order clique lexicographically
        for u in clique:
            u = self.node_lookup[u]
            for v in clique:
                v = self.node_lookup[v]

                if u < v:
                    self._add_clause(self.ord[u][v])
                    self._add_clause(self.arc[u][v])
