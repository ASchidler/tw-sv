"""Randomly assigns vertices to be CVertices"""

import os
import sys
import parse.ctw_parser as ps
import random

path = sys.argv[3]
sffx = sys.argv[2]
target = float(sys.argv[1])
random.seed = 1

for r, d, f in os.walk(path):
    for file in f:
        g, cv = ps.parse(os.path.join(r, file))
        if len(cv) > 0:
            print(f"{file} already has c-vertices, skipping...")
            continue

        vertices = list(g.nodes)
        for i in range(0, len(vertices)):
            # Randomly swap vertex
            idx = random.randint(i, len(vertices)-1)
            vertices[i], vertices[idx] = vertices[idx], vertices[i]

        # Determine how many vertices will become cvertices
        cverts = int(len(vertices) * target)
        if cverts == 0:
            cverts = 1

        with open(os.path.join(r, file), "r") as inp:
            with open(os.path.join(r, f"{file}{sffx}"), "w") as outp:
                outp.write(inp.read())
                outp.write("\n\nCVertices\n")
                for i in range(0, cverts):
                    outp.write(f"{vertices[i]}\n")

        print(f"Finished {file}")
