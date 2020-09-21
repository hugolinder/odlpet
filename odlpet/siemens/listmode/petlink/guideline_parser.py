from pathlib import Path
import packet
import numpy as np

def parse(x="./guideline.txt", encoding='utf-8'):
    with open(Path(x), 'rt', encoding=encoding) as fid:
        guideline = fid.read()
    hierarcy = ["[section]", "[subsection]", "[packet]"]
    sections = guideline.split("[section]")[1:]
    tree = {}
    for k, s in enumerate(sections):
        subs = s.split('[subsection]')[1:]
        names = [x.strip().split("\n")[0] for x in subs]
        packets = [x.split('[packet]')[1:] for x in subs]
        tree[k] = dict(zip(names, packets))
    return tree

def parse_packet(description):
    lines = description.split("\n")
    name = lines[0]
    partition = lines[1]
    visual_guide = lines[2]
    field_symbols = np.unique(partition.replace(" ", ""))
    variables = [x for x in field_symbols if (x not in "01")]
    if len(variables) == len(field_symbols):
        num_fields = len(variables)
    else:
        num_fields = len(variables) + 1 # assume only one fixed value field
    k = 3+num_fields
    field_descriptions = lines[3:k] 
    comment = None if k < len(lines) else "\n".join(lines[k:])




