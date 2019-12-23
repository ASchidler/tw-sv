import os
import re
from sys import maxsize
import sys

path = "/home/aschidler/Downloads/extended-results"
output1 = "ctw_results.csv"
output2 = "ctw_results2.csv"


class TwResult:
    def __init__(self, tw, twub, twlb):
        self.tw = tw
        self.twub = twub
        self.twlb = twlb

    def print(self, stream):
        stream.write(f";{self.tw};{self.twlb};{self.twub}")

    @classmethod
    def print_header(cls, stream, name):
        stream.write(f";{name} tw;{name} lower;{name} upper")


class CtwResult(TwResult):
    def __init__(self, c, clb, cub, tw, twub, twlb, c_vertices):
        super().__init__(tw, twub, twlb)
        self.clb = clb
        self.cub = cub
        self.c = c
        self.c_vertices = c_vertices

    def print(self, stream):
        super().print(stream)
        stream.write(f";{self.c_vertices};{self.c};{self.clb};{self.cub}")

    @classmethod
    def print_header(cls, stream, name):
        TwResult.print_header(stream, name)
        stream.write(f";{name} c_vertices; {name} c;{name} c lower; {name} c upper")


class ResultLine:
    """The results of a single instance"""
    def __init__(self, num_entries):
        self.num_entries = num_entries
        # General instance info
        self.nodes = None
        self.edges = None
        # The results from finding the treewidth
        self.tw_result = None
        # The results for finding the ctw on 10% and 5% instances, each for offsets 0 to num_entries-1
        self.ctw_entries = {x: [None for _ in range(0, num_entries)] for x in range(1, 3)}

    def print(self, stream):
        stream.write(f"{self.nodes};{self.edges}")
        if self.tw_result:
            self.tw_result.print(stream)
        else:
            stream.write(";;;")

        for i in range(1, 3):
            for entry in self.ctw_entries[i]:
                if entry:
                    entry.print(stream)
                else:
                    stream.write(";;;;;;;")

    @classmethod
    def print_header(cls, stream, num_entries):
        stream.write(";nodes;edges")
        TwResult.print_header(stream, "tw")
        for i in range(1, 3):
            for j in range(0, num_entries):
                CtwResult.print_header(stream, f"{10//i}% ctw{j}")


def parse_cfile(result, fl):
    """Parses a CTW results file"""
    cub = maxsize
    clb = 0
    twub = maxsize
    twlb = 0

    primed_tw = 0
    primed_c = 0

    c_verts = 0

    while True:
        line = fl.readline()
        if line is None or line == "":
            break

        if line.startswith("Graph has"):
            m = re.search("([0-9]+) nodes, ([0-9]+) edges and ([0-9]+) c-vertices", line)
            result.nodes = int(m.group(1))
            result.edges = int(m.group(2))
            c_verts = int(m.group(3))
        elif line.startswith("Lower bound"):
            m = re.search("C: ([0-9]+)", line)
            clb = int(m.group(1))
        elif line.startswith("Upper bound"):
            m = re.search("C: ([0-9]+), tree width ([0-9]+)", line)
            cub = int(m.group(1))
            twub = int(m.group(2))
        elif line.startswith("Looking"):
            m = re.search("size ([0-9]+), C: ([0-9]+)", line)
            primed_tw = int(m.group(1))
            primed_c = int(m.group(2))
        elif line.startswith("Found decomposition"):
            m = re.search("Found decomposition of size ([0-9]+)", line)
            twub = m.group(1)
            cub = primed_c
        elif line.startswith("Failed"):
            twlb = max(twlb, primed_tw + 1)
        elif line.startswith("Found tree width"):
            m = re.search("width ([0-9]+), C: ([0-9]+)", line)
            c = m.group(2)
            tw = m.group(1)
            return CtwResult(c, c, c, tw, tw, tw, c_verts)

    return CtwResult(None, clb, cub, None, twlb, twub, c_verts)


def parse_twfile(result, fl):
    twub = maxsize
    twlb = 0

    primed_tw = 0

    while True:
        line = fl.readline()
        if line is None or line == "":
            break

        if line.startswith("Graph has"):
            m = re.search("([0-9]+) nodes and ([0-9]+) edges", line)
            result.nodes = int(m.group(1))
            result.edges = int(m.group(2))
        elif line.startswith("Lower Bound"):
            m = re.search("Lower Bound: ([0-9]+)", line)
            twlb = int(m.group(1))
        elif line.startswith("Upper Bound"):
            m = re.search("Upper Bound: ([0-9]+)", line)
            twub = int(m.group(1))
        elif line.startswith("Looking"):
            m = re.search("of size ([0-9]+)", line)
            primed_tw = int(m.group(1))
        elif line.startswith("Found decomposition"):
            m = re.search("Found decomposition of size ([0-9]+)", line)
            twub = m.group(1)
        elif line.startswith("Failed"):
            twlb = max(twlb, primed_tw + 1)
        elif line.startswith("Found tree width"):
            m = re.search("width ([0-9]+)", line)
            tw = m.group(1)
            return TwResult(tw, tw, tw)

    return TwResult(None, twub, twlb)


results = {}
cnt = 0

for r, d, f in os.walk(path):
    for file in f:
        if file.endswith(".out"):
            m = re.search("/([^/]*)/0/?$", r)
            instance = m.group(1)
            # Instance generation went wrong with this single instance
            if instance.startswith("LabeledTest.dgf"):
                continue

            # Find out which result we have based on the instance name's file ending
            instance_type = 0
            if instance.endswith(".1"):
                instance_type = 1
                instance = instance[0:len(instance) - 2]
            elif instance.endswith(".05"):
                instance_type = 2
                instance = instance[0:len(instance) - 3]

            if instance not in results:
                results[instance] = ResultLine(6)
            resultobj = results[instance]

            with open(os.path.join(r, file), "r") as c_file:
                if instance_type == 0 and "/tw/" in r:
                    resultobj.tw_result = parse_twfile(resultobj, c_file)
                elif instance_type > 0 and "/ctw" in r:
                    m = re.search("/ctw([0-9])/", r)
                    offset = int(m.group(1))
                    resultobj.ctw_entries[instance_type][offset] = parse_cfile(resultobj, c_file)

                cnt += 1
                if cnt % 100 == 0:
                    print(f"Parsed {cnt} files")

# Output results
with open(output1, "w") as raw_file:
    with open(output2, "w") as aggregate_file:
        raw_file.write("instance")
        ResultLine.print_header(raw_file, 6)
        raw_file.write(os.linesep)

        aggregate_file.write("instance;solved;nodes;edges;tw;10 cvertices;10 c_min;10 c_max;10 tw_min;"
                             "10 tw_max;5 cvertices; 5 c_min;5 c_max;5 tw_min;5 tw_max")
        aggregate_file.write(os.linesep)

        for instance, c_line in results.items():
            # Output raw data
            raw_file.write(f"{instance};")
            c_line.print(raw_file)
            raw_file.write(os.linesep)

            # Aggregate
            solved = True
            c_output = None

            if not c_line.tw_result.tw:
                solved = False

            c_output = f"{instance};{solved};{c_line.nodes};{c_line.edges};"

            if not solved:
                c_output += ";;;;;;;;"
            if solved:
                c_output += f"{c_line.tw_result.tw}"

                for i in range(1, 3):
                    groups = c_line.ctw_entries[i]
                    min_c = groups[0].c
                    max_tw = groups[0].tw
                    max_c = None
                    min_tw = None
                    cv = groups[0].c_vertices

                    if not min_c or not max_tw:
                        c_output += ";;;;"
                        continue

                    found = False
                    for i in range(0, len(groups)):
                        if groups[i].tw:
                            if groups[i].tw == min_tw:
                                found = True
                                break
                            max_c = groups[i].c
                            min_tw = groups[i].tw

                    if found:
                        c_output += f";{cv};{min_c};{max_c};{min_tw};{max_tw}"
                    else:
                        c_output += ";;;;"

            c_output += os.linesep
            aggregate_file.write(c_output)
            sys.stdout.write(c_output)


