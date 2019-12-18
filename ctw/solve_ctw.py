import subprocess

import ctw.c_lower_bound as clb
import ctw.c_upper_bound as cb
import tw_utils
from ctw import c_sv as svc


def solve(g, c_vertices, inpf, outpf, offset=0, timeout=300):
    print(f"Graph has {len(g.nodes)} nodes, {len(g.edges)} edges and {len(c_vertices)} c-vertices")

    c_lb = clb.c_lower_bound(g, c_vertices)
    tub, cub, ordering = cb.min_c(g, c_vertices)
    print(f"Lower bound C: {c_lb}")
    print(f"Upper bound C: {cub}, tree width {tub}")

    # For c-treewidth we have to find the optimal c-value
    tlb = 1
    cval = tub-1
    knownc = cub
    cub += offset

    while tlb <= cval < tub:
        print(f"\nLooking for decomposition of size {cval}, C: {cub}")
        f2 = open(inpf, "w+")

        slv = svc.CTwEncoding(c_vertices, cub, f2, g)

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
                tub = max(len(cb) - 1 for cb in b.values())
                knownc = max(len(cb & c_vertices) for cb in b.values())
                cval = tub - 1
                print(f"Found decomposition of size {tub}, C: {knownc}")
            else:
                print("Failed to find decomposition")
                cval += 1
                tlb = cval

        except subprocess.TimeoutExpired:
            print(f"Timeout: Width is between {tlb} and {tub}")
            return -1, None

    print(f"\nFound tree width {tub}, C: {knownc}")
    return tub, ordering
