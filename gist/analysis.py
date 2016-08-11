import os
import utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('ggplot')

markers = {  # this is a copy from matplotlib.markers.py ...
        '.': 'point',
        # ',': 'pixel',
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
        # '+': 'plus',
        # 'x': 'x',
        'D': 'diamond',
        'd': 'thin_diamond',
        # '|': 'vline',
        # '_': 'hline',
        }.keys()


def mask(df, key, value):
    return df[df[key] == value]

pd.DataFrame.mask = mask

df = pd.read_csv("tests/ember_output/100k_summary.csv")
# TODO this feels like a pretty dangers fix...
df = df.replace(np.nan, -1)

x_tick_key = "num_nics"
plot_group_keys = ["work_load", "messageSize", "iteration", "messagesize"]
y_value_keys = ["exe_time(us)", "real_latency(us)", "real_bandwidth(GB/s)"]

plot_groups = df.groupby(plot_group_keys)
plot_cnt = 0
# each of this group should be in a separate plot
for metric in y_value_keys:
    for plot_keys, each_plot_group in plot_groups:
        print plot_keys[0]
        # if needed, add sub_plot groups
        fig, ax = plt.subplots(1, 1)
        line_groups = each_plot_group.groupby(["topo"])
        line_cnt = 0
        labels = []
        # each of this group should be a line in plot
        for line_keys, each_line_group in line_groups:
            group = each_line_group.sort(x_tick_key)
            if all(group["topo"] == "torus"):
                sub_groups = group.groupby(group["shape"].str.count("x"))
                for count, sub_group in sub_groups:
                    topo = "torus-%dD" % (count + 1)
                    labels.append(topo)
                    sub_group["topo"] = topo
                    if not any(sub_group[metric] == -1):
                        ax.plot(sub_group[x_tick_key], sub_group[metric],
                                linewidth=2, marker=markers[line_cnt], markersize=8)
                    line_cnt += 1
            elif all(group["topo"] == "fattree"):
                sub_groups = group.groupby(group["shape"].str.count(":"))
                for count, sub_group in sub_groups:
                    topo = "fattree-%d" % (count + 1)
                    labels.append(topo)
                    sub_group["topo"] = topo
                    if not any(sub_group[metric] == -1):
                        ax.plot(sub_group[x_tick_key], sub_group[metric],
                                linewidth=2, marker=markers[line_cnt], markersize=8)
                    line_cnt += 1
            else:
                topo = group["topo"].iloc[0]
                labels.append(topo)
                if not any(group[metric] == -1):
                    ax.plot(group[x_tick_key], group[metric],
                            linewidth=2, marker=markers[line_cnt], markersize=8)
                line_cnt += 1
        title_text = ""
        key_cnt = 0
        for key in plot_group_keys:
            title_text += "%s=%s_" % (key, str(plot_keys[key_cnt]))
            key_cnt += 1
        ax.set_title(title_text)
        ax.legend(labels, loc="best")
        ax.set_xlabel(x_tick_key)
        ax.set_ylabel(metric)
        output_name = "plot_%d.png" % plot_cnt

        output_dir = os.path.join("graphs", utils.replace_special_char(metric))
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_name = os.path.join(output_dir, output_name)
        plot_cnt += 1
        fig.savefig(output_name, format="png")
        fig.clf()
        plt.close(fig)

