import argparse
import os

import ctw.solve_ctw as solve_ctw
import parse.ctw_parser as ps
import solve_tw
import signal

parser = argparse.ArgumentParser(description='Calculates the treewidth of a graph. Support C-Treewidth')
parser.add_argument('graph', metavar='graph_file', type=str, help='The input file containing the graph')
parser.add_argument('-c', dest='ctw', action='store_true', default=False, help='Treat as c-treewidth instance')
parser.add_argument('-o', dest='offset', type=int, default=0, choices=range(0, 10), help='Use minimal c + offset')

args = parser.parse_args()

g, c_vertices = ps.parse(args.graph)
is_ctw = args.ctw


def terminateProcess():
    if os.path.exists(filename):
        os.remove(filename)
    if os.path.exists(fileout):
        os.remove(fileout)

    exit(1)


signal.signal(signal.SIGTERM, terminateProcess)

# Upper bound is already a solution, so look starting from ub - 1
filename = f"{os.getpid()}_encoding.txt"
fileout = f"{os.getpid()}_result.txt"

def terminateProcess():
    if os.path.exists(filename):
        os.remove(filename)
    if os.path.exists(fileout):
        os.remove(fileout)


signal.signal(signal.SIGTERM, terminateProcess)

if (is_ctw and len(c_vertices) == 0) or (not is_ctw and len(c_vertices) > 0):
    exit(2)

try:
    ret, _ = solve_ctw.solve(g, c_vertices, filename, fileout, offset=args.offset) if is_ctw \
        else solve_tw.solve(g, filename, fileout)
finally:
    if os.path.exists(filename):
        os.remove(filename)
    if os.path.exists(fileout):
        os.remove(fileout)

if ret < 0:
    exit(1)


