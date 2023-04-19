import upper_bounds as ubs
import lower_bounds as lbs
import sv_improved as svi
import tw_utils
import sys
from pysat.solvers import Glucose3

def solve(g):
    print(f"Graph has {len(g.nodes)} nodes and {len(g.edges)} edges")
    ub, ordering = ubs.greedy_min_degree(g)
    lb = lbs.lbnp(g)

    print(f"Upper Bound: {ub}")
    print(f"Lower Bound: {lb}")
    sys.stdout.flush()

    cval = ub - 1

    # Incrementally search
    while lb <= cval < ub:
        print(f"\nLooking for decomposition of size {cval}")
        enc = svi.ImprovedSvEncoding(g)
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
                ub = max(len(cb) - 1 for cb in b.values())

                cval = ub - 1
                print(f"Found decomposition of size {ub}")
                sys.stdout.flush()
            else:
                print("Failed to find decomposition")
                sys.stdout.flush()
                cval += 1
                lb = cval

    print(f"\nFound treewidth {ub}")
    sys.stdout.flush()
    return ub, ordering
