import sv
import networkx.algorithms.clique as cq


class ImprovedSvEncoding(sv.SvEncoding):
    """Improvements upon the Samer-Veith encoding"""
    def encode(self):
        #self.encode_cliques()
        super().encode()

        # Not strictly necessary, but speedup
        # for i in range(0, len(self.g.nodes)):
        #     for j in range(i+1, len(self.g.nodes)):
        #         self._add_clause(-self.arc[j][i], -self.arc[i][j])

    def encode_cliques(self):
        """Enforces lexicographical ordering of the cliques"""

        # order cliques lexicographically
        for clique in cq.find_cliques(self.g):
            # Edges do not constitute a clique for this purpose
            if len(clique) < 3:
                continue

            for u in clique:
                u = self.node_lookup[u]
                for v in clique:
                    v = self.node_lookup[v]

                    if u < v:
                        self._add_clause(self.ord[u][v])
                        # Also add arcs already?
