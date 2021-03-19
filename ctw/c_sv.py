import sv_improved as sv


class CTwEncoding(sv.ImprovedSvEncoding):
    """Extends the base treewidth encoding with cardinality constraints for heavy vertices"""
    def __init__(self, reds, red_limit, stream, g):
        super().__init__(stream, g)
        self.reds = {self.node_lookup[x] for x in reds}
        self.red_limit = red_limit

    def encode(self):
        super().encode()
        self.encode_c_counter(self.red_limit)

    def encode_c_counter(self, c):
        # Add dummy-var that is always true, see below for use
        t_var = self._add_var()
        self._add_clause(t_var)

        rlist = list(self.reds)
        target_variables = [list() for _ in range(0, len(self.g.nodes))]

        n = 0
        for d in target_variables:
            for u in rlist:
                # If n is red, it is in its own bag. This construct counts this. Otherwise, since arc[n][n] is always
                # false, the red goes uncounted
                if n == u and n in self.reds:
                    d.append(t_var)
                else:
                    d.append(self.arc[n][u])
            n += 1

        self.encode_cardinality_sat(c, target_variables)
