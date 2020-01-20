import subprocess

import ctw.c_lower_bound as clb
import ctw.c_upper_bound as cb
import tw_utils
import sys
from ctw import c_sv as svc
import sys


def solve_c(g, c_vertices, inpf, outpf, timeout=1800):
    c_lb = clb.c_lower_bound(g, c_vertices)
    tub, cub, ordering = cb.min_c(g, c_vertices)
    val = cub - 1
    t_val = None
    while c_lb <= val < cub:
        print(f"\nLooking for decomposition of with C: {cub}")
        f2 = open(inpf, "w+")
        slv = svc.CTwEncoding(c_vertices, cub, f2, g)

        slv.encode_sat(0, cardinality=False)
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
                cub = max(len(cb & c_vertices) for cb in b.values())
                t_val = max(len(cb) - 1 for cb in b.values())
                val = cub - 1
                print(f"Found decomposition, C: {cub}")
                sys.stdout.flush()
            else:
                print("Failed to find decomposition")
                sys.stdout.flush()
                break

        except subprocess.TimeoutExpired:
            print(f"Timeout")
            sys.stdout.flush()
            return None
    return cub, t_val


def solve(g, c_vertices, inpf, outpf, c_val, tub=None, timeout=1800):
    if len(c_vertices) == 0:
        return -1, None
    print(f"Graph has {len(g.nodes)} nodes, {len(g.edges)} edges and {len(c_vertices)} c-vertices")

    if tub is None:
        tub, cub, ordering = cb.min_c(g, c_vertices)
    print(f"Upper bound C: {c_val}, tree width {tub}")
    sys.stdout.flush()

    # For c-treewidth we have to find the optimal c-value
    tlb = 1
    cval = tub-1
    knownc = c_val

    while tlb <= cval < tub:
        print(f"\nLooking for decomposition of size {cval}, C: {c_val}")
        f2 = open(inpf, "w+")

        slv = svc.CTwEncoding(c_vertices, c_val, f2, g)

        # TODO: Insert a spaceholder for the header, to be overwritten later, i.e. use upper bounds for the number of variables and clauses...
        slv.encode_sat(cval, cardinality=True)
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

        except subprocess.TimeoutExpired:
            print(f"Timeout: Width is between {tlb} and {tub}")
            sys.stdout.flush()
            return -1, None

    print(f"\nFound tree width {tub}, C: {knownc}")
    sys.stdout.flush()
    return tub, ordering
