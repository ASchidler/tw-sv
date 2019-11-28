from collections import defaultdict
import os


class SelfNamingDict(defaultdict):
    def __init__(self, cb, name=None):
        super().__init__()
        self.name = name
        self.callback = cb

    def __missing__(self, key):
        if self.name is None:
            val = self.callback()
        else:
            val = self.callback(self.name.format(key))

        self[key] = val
        return val


class SvEncoding:
    def __init__(self, stream, g):
        self.g = g
        self.ord = None
        self.arc = None
        self.vars = [None]  # None to avoid giving any var 0
        self.var_literal = None
        self.clause_literal = "{} 0"
        self.clause_literal_fun = lambda x: self.vars[x] if x > 0 else f"-{self.vars[-x]}"
        self.stream = stream
        self.nodes = list(g.nodes)
        self.node_lookup = {self.nodes[n]: n for n in range(0, len(self.nodes))}
        self.num_clauses = 0

    def _add_var(self, nm=None):
        self.vars.append(nm if nm is not None else str(len(self.vars)))
        if self.var_literal is not None:
            self.stream.write(self.var_literal.format(self.vars[len(self.vars) - 1]))
            self.stream.write("\n")

        return len(self.vars) - 1

    def _add_clause(self, *args):
        self.stream.write(self.clause_literal.format(' '.join((self.clause_literal_fun(x) for x in args))))
        self.stream.write("\n")
        self.num_clauses += 1

    def _ord(self, i, j):
        if i < j:
            return self.ord[i][j]
        else:
            return -1 * self.ord[j][i]

    def encode(self):
        for i in range(0, len(self.g.nodes)):
            # No self loops
            self._add_clause(-self.arc[i][i])

            for j in range(0, len(self.g.nodes)):
                if i == j:
                    continue
                for l in range(0, len(self.g.nodes)):
                    if i == l or j == l:
                        continue

                    # Transitivity of ordering
                    self._add_clause(-self._ord(i, j), -self._ord(j, l), self._ord(i, l))

                    # Additional edges due to linear ordering
                    if j < l:
                        # ord instead of _ord is on purpose in both clauses
                        self._add_clause(-self.arc[i][j], -self.arc[i][l], -self.ord[j][l], self.arc[j][l])
                        self._add_clause(-self.arc[i][j], -self.arc[i][l], self.ord[j][l], self.arc[l][j])

                        # Redundant, but speeds up solving
                        self._add_clause(-self.arc[i][j], -self.arc[i][l], self.arc[j][l], self.arc[l][j])

        # Encode edges
        for u, v in self.g.edges:
            u = self.node_lookup[u]
            v = self.node_lookup[v]
            if u < v:
                self._add_clause(-self.ord[u][v], self.arc[u][v])
                self._add_clause(self.ord[u][v], self.arc[v][u])

    def encode_smt(self, g, stream, lb=0, ub=0):
        self.ord = {x: SelfNamingDict(lambda x: self._add_var(x), f"ord_{x}_{{}}") for x in range(0, len(g.nodes))}
        self.arc = {x: SelfNamingDict(lambda x: self._add_var(x), f"arc_{x}_{{}}") for x in range(0, len(g.nodes))}
        self.stream.write("(set-option :produce-models true)")
        self.var_literal = "(declare-const {} Bool)"
        self.clause_literal = "(assert (or {}))"
        self.clause_literal_fun = lambda x: self.vars[x] if x > 0 else f"(not {self.vars[-x]})"

        stream.write("(declare-const m Int)\n")
        stream.write("(assert (>= m 1))\n")
        if lb > 0:
            stream.write(f"(assert (>= m {lb}))\n")
        if ub > 0:
            stream.write(f"(assert (<= m {ub}))\n")

        self.encode()
        #self.encode_cardinality_smt(ub)
        self.encode_cardinality_sat(ub-4, self.arc)

        # stream.write("(minimize m)\n")
        stream.write("(check-sat)\n")
        stream.write("(get-model)\n")

    def encode_sat(self, target):
        tmp_stream = self.stream
        self.stream = open("tmp_sat.txt", "w")
        self.ord = {x: SelfNamingDict(lambda: self._add_var()) for x in range(0, len(self.g.nodes))}
        self.arc = {x: SelfNamingDict(lambda: self._add_var()) for x in range(0, len(self.g.nodes))}

        self.encode()
        self.encode_cardinality_sat(target, self.arc)

        self.stream.close()
        self.stream = tmp_stream

        self.stream.write(f"p cnf {len(self.vars) - 1} {self.num_clauses}\n")
        tmp_stream = open("tmp_sat.txt")
        self.stream.write(tmp_stream.read())
        tmp_stream.close()

        os.remove("tmp_sat.txt")

    def encode_cardinality_smt(self, ub):
        for i in range(0, len(self.g.nodes)):
            vars = []
            for j in range(0, len(self.g.nodes)):
                if i == j:
                    continue

                arcvar = self.vars[self.arc[i][j]]
                # stream.write(f"(declare-const w_{i}_{j} Int)\n")
                # stream.write(f"(assert (=> {arcvar} (= w_{i}_{j} 1)))\n")
                # stream.write(f"(assert (=> (not {arcvar}) (= w_{i}_{j} 0)))\n")
                #vars.append(f"(ite {arcvar} 1 0)")
                vars.append(arcvar)
                self.stream.write(f"(assert-soft (not {arcvar}) :id goal{i})\n")
            self.stream.write(f"(assert (<= goal{i} m))\n")

            #self.stream.write("(assert ((_ at-most {ub}) {weights}))\n".format(ub=ub, weights=" ".join(vars)))

    def encode_cardinality_sat(self, bound, variables):
        """Enforces cardinality constraints. Cardinality of 2-D structure variables must not exceed bound"""
        # Define counter variables
        ctr = [[[self._add_var()
                 for l in range(0, min(j, bound))]
                for j in range(1, len(self.g.nodes))]
               for i in range(0, len(self.g.nodes))]

        for i in range(0, len(self.g.nodes)):
            for j in range(1, len(self.g.nodes) - 1):
                for l in range(0, min(j, bound)):
                    # Ensure counter never decrements
                    self._add_clause(-ctr[i][j - 1][l], ctr[i][j][l])

                    # Carry over from previous column
                    if l > 0:
                        self._add_clause(-variables[i][j], -ctr[i][j-1][l-1], ctr[i][j][l])

        # Increment counter
        for i in range(0, len(self.g.nodes)):
            for j in range(1, len(self.g.nodes) - 1):
                self._add_clause(-variables[i][j], ctr[i][j][0])

        # Conflict if target is exceeded
        for i in range(0, len(self.g.nodes)):
            for j in range(bound, len(self.g.nodes) - 1):
                self._add_clause(-variables[i][j], -ctr[i][j-1][bound - 1])
