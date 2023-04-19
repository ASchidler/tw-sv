import subprocess

import ctw.c_lower_bound as clb
import ctw.c_upper_bound as cb
import tw_utils
import sys
from ctw import c_sv as svc
import sys
from pysat.solvers import Glucose3


def solve_c(g, c_vertices, tub, c_value):
    c_lb = clb.c_lower_bound(g, c_vertices)
    print(f"C lower bound {c_lb}")
    val = c_value - 1
    ordering = None

    while c_lb <= val < c_value:
        print(f"\nLooking for decomposition of width C: {val}")

        enc = svc.CTwEncoding(c_vertices, val, g)
        enc.encode()
        enc.encode_card(tub)

        with Glucose3() as slv:
            slv.append_formula(enc.formula)
            result = slv.solve()
            if result:
                model = {abs(x): x > 0 for x in slv.get_model()}
                ordering = []

                for i in range(0, len(g.nodes)):
                    pos = 0
                    for j in ordering:
                        if not model[enc._ord(j, i)]:
                            break
                        pos += 1

                    ordering.insert(pos, i)

                # Translate encoder indexing
                ordering = [enc.nodes[x] for x in ordering]

                b, t, r = tw_utils.ordering_to_decomp(g, ordering)
                # Check actual size of decomposition and proceed accordingly
                tub = max(len(cb) - 1 for cb in b.values())
                knownc = max(len(cb & c_vertices) for cb in b.values())
                val = knownc - 1
                print(f"Found decomposition of size {tub}, C: {knownc}")
                sys.stdout.flush()
            else:
                print("Failed to find decomposition")
                sys.stdout.flush()
                val += 1

        print(f"\nFound tree width {tub}, C: {knownc}")
        sys.stdout.flush()
        return tub, ordering

    return val, tub, ordering


def solve(g, c_vertices, tub=None):
    if len(c_vertices) == 0:
        return -1, None
    print(f"Graph has {len(g.nodes)} nodes, {len(g.edges)} edges and {len(c_vertices)} c-vertices")

    tub2, c_val, ordering = cb.min_c(g, c_vertices)
    if tub is None or tub2 < tub:
        tub = tub2

    tub2, val, ordering2 = solve_c(g, c_vertices, tub, c_val)
    if ordering2 is not None:
        c_val = val
        tub = tub2
        ordering = ordering2

    print(f"Upper bound C: {c_val}, tree width {tub}")
    sys.stdout.flush()

    # For c-treewidth we have to find the optimal c-value
    tlb = 1
    cval = tub-1
    knownc = c_val

    while tlb <= cval < tub:
        print(f"\nLooking for decomposition of size {cval}, C: {c_val}")
        enc = svc.CTwEncoding(c_vertices, c_val, g)
        enc.encode()
        enc.encode_card(cval)

        with Glucose3() as slv:
            slv.append_formula(enc.formula)
            result = slv.solve()
            if result:
                model = {abs(x): x > 0 for x in slv.get_model()}
                ordering = []

                for i in range(0, len(g.nodes)):
                    pos = 0
                    for j in ordering:
                        if not model[enc._ord(j, i)]:
                            break
                        pos += 1

                    ordering.insert(pos, i)

                # Translate encoder indexing
                ordering = [enc.nodes[x] for x in ordering]

                b, t, r = tw_utils.ordering_to_decomp(g, ordering)
                # Check actual size of decomposition and proceed accordingly
                tub = max(len(cb) - 1 for cb in b.values())
                knownc = max(len(cb & c_vertices) for cb in b.values())
                cval = tub - 1
                print(f"Found decomposition of size {tub}, C: {knownc}")
                sys.stdout.flush()
            else:
                print("Failed to find decomposition")
                sys.stdout.flush()
                cval += 1
                tlb = cval

    print(f"\nFound tree width {tub}, C: {knownc}")
    sys.stdout.flush()
    return tub, ordering
