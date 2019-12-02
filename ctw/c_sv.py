import sv_improved as sv


class CTwEncoding(sv.ImprovedSvEncoding):
    def __init__(self, reds, red_limit, stream, g):
        super().__init__(stream, g)
        self.reds = {self.node_lookup[x] for x in reds}
        self.red_limit = red_limit

    def encode(self):
        super().encode()
        self.encode_c_counter(self.red_limit)

    def encode_c_counter(self, c):
        rlist = list(self.reds)
        target_variables = [list() for _ in range(0, len(self.g.nodes))]

        n = 0
        for d in target_variables:
            for u in rlist:
                d.append(self.arc[n][u])
            n += 1

        self.encode_cardinality_sat(c, target_variables)
