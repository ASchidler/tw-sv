import argparse

import ctw.ctw_parser as ps
import ctw.solve_ctw as solve_ctw
import solve_tw
import sv_improved as svi
from pysat.formula import WCNF
import upper_bounds as ubs

parser = argparse.ArgumentParser(description='Calculates the treewidth of a graph. Support C-Treewidth')
parser.add_argument('graph', metavar='graph_file', type=str, help='The input file containing the graph')
parser.add_argument('-c', dest='ctw', action='store_true', default=False, help='Treat as c-treewidth instance')
parser.add_argument('-o', dest='offset', type=int, default=0, choices=range(0, 10), help='Use minimal c + offset')
parser.add_argument("-m", dest='maxsat', type=str, default=None, help="Write MaxSAT encoding to file.")
parser.add_argument("-d", dest="sep_cards", action="store_true", default=False, help="Store cardinalities separately")

args = parser.parse_args()

g, c_vertices = ps.parse(args.graph)
is_ctw = args.ctw

if (is_ctw and len(c_vertices) == 0) or (not is_ctw and len(c_vertices) > 0):
    exit(2)

if args.maxsat is None:
    ret, _ = solve_ctw.solve(g, c_vertices) if is_ctw \
        else solve_tw.solve(g)

    if ret < 0:
        exit(1)
else:
    enc = svi.ImprovedSvEncoding(g)
    enc.encode()
    if args.sep_cards:
        enc.formula.to_file(args.maxsat)
        enc.encode_card(None, args.maxsat + ".cards")
    else:
        cub, _ = ubs.greedy_min_degree(g)
        enc.as_maxsat(cub).to_file(args.maxsat)

