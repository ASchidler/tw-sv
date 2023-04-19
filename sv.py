from collections import defaultdict
import os
from pysat.formula import IDPool, CNF, WCNF
from pysat.card import CardEnc, ITotalizer


class SvEncoding:
    def __init__(self, g):
        self.g = g
        self.nodes = list(g.nodes)
        self.nodes.sort()
        self.node_lookup = {x: i for i, x in enumerate(self.nodes)}
        self.formula = CNF()
        self.pool = IDPool()

    def _ord(self, i, j):
        if i < j:
            return self.pool.id(f"ord_{i}_{j}")
        else:
            return -1 * self.pool.id(f"ord_{j}_{i}")
        
    def _arc(self, i, j):
        return self.pool.id(f"arc_{i}_{j}")

    def encode(self):
        for i in range(0, len(self.g.nodes)):
            # No self loops
            self.formula.append([-self._arc(i, i)])

            for j in range(0, len(self.g.nodes)):
                if i == j:
                    continue
                for k in range(0, len(self.g.nodes)):
                    if i == k or j == k:
                        continue

                    # Transitivity of ordering
                    self.formula.append([-self._ord(i, j), -self._ord(j, k), self._ord(i, k)])

                    # Additional edges due to linear ordering
                    if j < k:
                        self.formula.append([-self._arc(i, j), -self._arc(i, k), -self._ord(j, k), self._arc(j, k)])
                        self.formula.append([-self._arc(i, j), -self._arc(i, k), self._ord(j, k), self._arc(k, j)])

                        # Redundant, but speeds up solving
                        self.formula.append([-self._arc(i, j), -self._arc(i, k), self._arc(j, k), self._arc(k, j)])

        # Encode edges
        for u, v in self.g.edges:
            u = self.node_lookup[u]
            v = self.node_lookup[v]

            self.formula.append([-self._ord(u, v), self._arc(u, v)])
            self.formula.append([self._ord(u, v), self._arc(v, u)])
    
    # def export_smt(self, g, fname, lb=0, ub=0):
    #     with open(fname, "w") as outp:
    #         outp.write("(set-option :produce-models true)")
    #         for cid, cobj in self.pool.id2obj.items():
    #             outp.write(f"(declare-const {cobj} Bool)\n")
    #             outp.write("(declare-const m Int)\n")
    #             outp.write("(assert (>= m 1))\n")
    #
    #         if lb > 0:
    #             outp.write(f"(assert (>= m {lb}))\n")
    #         if ub > 0:
    #             outp.write(f"(assert (<= m {ub}))\n")
    #
    #         for c_cl in self.formula.clauses:
    #             c_vars = [self.pool.obj(x) if x > 0 else f"(not {self.pool.obj(-x)})" for x in c_cl]
    #             outp.write(f"(assert (or {' '.join(c_vars)}))")
    #
    #         outp.write("(check-sat)\n")
    #         outp.write("(get-model)\n")

    def export_sat(self, fname):
        self.formula.to_file(fname)
        
    def encode_card(self, d, fname=None):
        if fname is None:
            for cn in range(0, len(self.g.nodes)):
                self.formula.extend(CardEnc.atmost([self._arc(cn, x) for x in range(0, len(self.g.nodes))], d, vpool=self.pool))
        else:
            with open(fname, "w") as outp:
                for cn in range(0, len(self.g.nodes)):
                    outp.write(" ". join([str(self._arc(cn, x)) for x in range(0, len(self.g.nodes))]))
                    outp.write(" <= d" + os.linesep)

    def as_maxsat(self, d):
        formula = WCNF()
        formula.extend(self.formula)
        softs = [self.pool.id(f"softs_{i}") for i in range(1, d+1)]

        for cs in softs:
            formula.append([-cs], 1)

        for cn in range(0, len(self.g.nodes)):
            with ITotalizer([self._arc(cn, x) for x in range(0, len(self.g.nodes))], d, self.pool.top) as itot:
                self.pool.occupy(self.pool.top, itot.top_id)
                formula.extend(itot.cnf)
                for i in range(1, d+1):
                    formula.append([-itot.rhs[i], softs[i-1]])

        return formula
