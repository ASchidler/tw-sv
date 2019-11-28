import sv_improved as sv


class CTwEncoding(sv.ImprovedSvEncoding):
    def __init__(self, reds, stream, g):
        super().__init__(stream, g)
        self.reds = {self.node_lookup[x] for x in reds}

    def encode_c_counter(self, c):
        target_variables = [dict() for _ in range(0, len(self.g.nodes))]

        n = 0
        for d in target_variables:
            for u in self.reds:
                d[u] = self.arc[n][u]
            n += 1

        self.encode_cardinality_sat(c, target_variables)
