import os
import bz2

# Path to search for instances
path = "/home/aschidler/Downloads/graphs-master/treewidth_benchmarks/twlib-graphs/twlib-graphs"
# Path to output the instances that match criteria
outpath = "/home/aschidler/Downloads/twlib-filtered"


def verify_file(str, filename):
    keep = False

    for cnt, line in enumerate(str):
        try:
            line = line.decode('ascii')
        except AttributeError:
            pass

        if line.startswith("p "):
            # The syntax is: p <problem> <vertices#> <edges#>
            values = line.split()
            try:
                verts = int(values[2])
                edges = int(values[3])

                # Check graph dimensions
                if 5 <= verts <= 100 and 1 <= edges <= 500:
                    keep = True
                    break
            except ValueError:
                return False

    # If p line found, write file to output
    if keep:
        str.seek(0)
        with open(filename, "w") as outp:
            for cnt, line in enumerate(str):
                outp.write(line.decode('ascii'))

    return keep


# Search for files and unpack if necessary
for r, d, f in os.walk(path):
    for file in f:
        full = os.path.join(r, file)
        if file.lower().endswith(".bz2"):
            with bz2.open(full, mode='rb') as b:
                verify_file(b, os.path.join(outpath, file.replace(".bz2", "")))
        else:
            with open(full, "r") as cf:
                verify_file(cf, os.path.join(outpath, file))
