import sv_improved as sv
from pysat.card import CardEnc

class CTwEncoding(sv.ImprovedSvEncoding):
    """Extends the base treewidth encoding with cardinality constraints for heavy vertices"""
    def __init__(self, reds, red_limit, g):
        super().__init__(g)
        self.reds = {self.node_lookup[x] for x in reds}
        self.red_limit = red_limit

    def encode(self):
        super().encode()
        self.encode_c_counter(self.red_limit)

    def encode_c_counter(self, c):
        # Add dummy-var that is always true, see below for use
        t_var = self.pool.id("t_var")
        self.formula.append([t_var])

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
                    d.append(self._arc(n, u))
            n += 1

            self.formula.extend(CardEnc.atmost(d, c, vpool=self.pool))
