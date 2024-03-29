import upper_bounds as ubs
import lower_bounds as lbs
import sv_improved as svi
import subprocess
import tw_utils
import sys


def solve(g, inpf, outpf, timeout=1800):
    print(f"Graph has {len(g.nodes)} nodes and {len(g.edges)} edges")
    ub, ordering = ubs.greedy_min_degree(g)
    lb = lbs.lbnp(g)

    print(f"Upper Bound: {ub}")
    print(f"Lower Bound: {lb}")
    sys.stdout.flush()

    cval = ub - 1
    lb_done = False

    # Incrementally search
    while lb <= cval < ub:
        print(f"\nLooking for decomposition of size {cval}")
        f2 = open(inpf, "w+")

        slv = svi.ImprovedSvEncoding(f2, g)

        # TODO: Insert a spaceholder for the header, to be overwritten later, i.e. use upper bounds for the number of variables and clauses...
        slv.encode_sat(cval)
        f2.close()
        p1 = subprocess.Popen(['minisat', '-verb=0', inpf, outpf], stdout=None, stderr=None)
        try:
            p1.wait(timeout)

            if p1.returncode == 10:
                ordering = tw_utils.minisat_extract_ordering(outpf, len(g.nodes))
                # Translate encoder indexing
                ordering = [slv.node_reverse_lookup[x] for x in ordering]
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

        except subprocess.TimeoutExpired:
            # If Timeout exceeded, try other direction
            if not lb_done:
                print("Timeout: Restarting from lower bound")
                sys.stdout.flush()
                lb_done = True
                cval = lb
            else:
                print(f"Timeout: Width is between {lb} and {ub}")
                sys.stdout.flush()
                return -1, None

    print(f"\nFound tree width {ub}")
    sys.stdout.flush()
    return ub, ordering
