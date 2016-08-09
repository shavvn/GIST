import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('ggplot')

markers = {  # this is a "hard copy" from matplotlib.markers.py ...
        '.': 'point',
        ',': 'pixel',
        'o': 'circle',
        'v': 'triangle_down',
        '^': 'triangle_up',
        '<': 'triangle_left',
        '>': 'triangle_right',
        '1': 'tri_down',
        '2': 'tri_up',
        '3': 'tri_left',
        '4': 'tri_right',
        '8': 'octagon',
        's': 'square',
        'p': 'pentagon',
        '*': 'star',
        'h': 'hexagon1',
        'H': 'hexagon2',
        '+': 'plus',
        'x': 'x',
        'D': 'diamond',
        'd': 'thin_diamond',
        '|': 'vline',
        '_': 'hline',
        }.keys()


def mask(df, key, value):
    return df[df[key] == value]

pd.DataFrame.mask = mask

df = pd.read_csv("tests/ember_output/summary.csv")

plot_groups = df.groupby(["work_load", "messageSize", "iteration"])

groups = df.groupby(["topo", "work_load", "messageSize", "iteration"])

for keys, group in groups:
    print keys
    group = group.sort("num_nics")
    if all(group["topo"] == "torus"):
        sub_groups = group.groupby(group["shape"].str.count("x"))
        for count, sub_group in sub_groups:
            topo = "torus-%dD" % (count + 1)
            sub_group["topo"] = topo
            print count
    elif all(group["topo"] == "fattree"):
        sub_groups = group.groupby(group["shape"].str.count(":"))
        for count, sub_group in sub_groups:
            topo = "fattree-%d" % (count + 1)
            sub_group["topo"] = topo
            print count
    else:
        pass

# df = df.mask("topo", "torus").mask("work_load", "AllPingPong").mask("messageSize", 10000.0).mask("iteration", 10)

grouped = df.groupby(df["shape"].str.count('x'))

cnt = 0
for count, group in grouped:
    print count
    print group.sort("num_nics")
    plt.plot(group["num_nics"], group["exe_time(us)"], marker=markers[cnt])

print grouped

torus_3d = df[df["shape"].str.count("x") == 3]
# torus_3d = df[df["shape"].str.contains(r'\d*x\d*x\d*')].sort("num_nics")
torus_2d = df[df["shape"].str.contains(r'\A\d*x\d*\Z')].sort("num_nics")

print torus_3d
print torus_2d


print "done"
# torus_2d["exe_time(us)"].plot(xticks=torus_2d["num_nics"])
# torus_3d["exe_time(us)"].plot(xticks=torus_2d["num_nics"])

