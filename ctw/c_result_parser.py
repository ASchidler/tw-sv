import sys
import os
from collections import defaultdict

path = sys.argv[1]
output_path = sys.argv[2]

ratios = ["05", "10", "20", "30"]


def vts(val):
    return "{}".format(val) if val is not None and val < sys.maxsize else ""


class RunResult:
    def __init__(self):
        self.min_c = None
        self.max_w = None
        self.max_c = None
        self.base_c = None


class TypeResult:
    def __init__(self):
        self.width = None
        self.results = [RunResult() for _ in ratios]


instance_results = defaultdict(TypeResult)

for r, d, f in os.walk(path):
    for file in f:
        # Only out files contain results
        if not file.endswith(".result"):
            continue

        f_param = file.split('.')
        ratio = f_param[-2]

        instance_name = ".".join(f_param[0:-2])
        instance_obj = instance_results[instance_name]
        run_result = instance_results[instance_name].results[ratios.index(ratio)]

        with open(os.path.join(r, file), "r") as cf:
            for i, line in enumerate(cf):
                vals = line.split()
                if len(vals) != 5:
                    continue

                c_w = int(vals[2])
                c_c = int(vals[4])

                if vals[0] == "t":
                    if instance_obj.width is not None and instance_obj.width != c_w:
                        print(f"Error: {instance_name} width was {instance_obj.width} should be set to {c_w}")
                    instance_obj.width = c_w
                    run_result.base_c = c_c
                elif vals[0] == "0":
                    run_result.min_c = c_c
                    run_result.max_w = c_w
                    run_result.max_c = c_c
                else:
                    run_result.max_c = max(run_result.max_c, c_c)

with open(output_path, "w+") as op:
    # Write header
    op.write("instance;width")

    for rt in ratios:
        op.write(";{rt}% obl c;{rt}% min c;{rt}% max c;{rt}% max width".format(rt=rt))
    op.write(os.linesep)

    # Write results
    for instance, results in instance_results.items():
        op.write(instance + ";" + vts(results.width))

        for rr in results.results:
            op.write(f";{vts(rr.base_c)};{vts(rr.min_c)};{vts(rr.max_c)};{vts(rr.max_w)}")
        op.write(os.linesep)
