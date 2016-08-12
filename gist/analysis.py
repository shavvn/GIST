import os
import utils
import pandas as pd
import matplotlib.pyplot as plt


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


def separate_topos(df):
    """
    This is sst specific stuff, since torus and fattree should be
    separated based on their shape (dimensions, levels)
    :param df: input df
    :return: df with finer grained topology classification
    e.g. torus-3d, torus-2d
    """
    x_s = df["shape"].str.count("x").unique()
    for x in x_s:
        if x > 0:
            df.ix[(df["topo"] == "torus") & (df["shape"].str.count("x") == x),
                  "topo"] = "torus_%d" % (x + 1)
    colon_s = df["shape"].str.count(":").unique()
    for x in colon_s:
        if x > 0:
            df.ix[(df["topo"] == "fattree") & (df["shape"].str.count(":") == x),
                  "topo"] = "fattree_%d" % (x + 1)
    return df


def cal_dragonfly_radix(shape_str):
    """
    This works for dragonfly shapes formatted as
    PxHxA
    :param shape_str: "PxHxA"
    :return: radix
    """
    nums = shape_str.split("x")
    nums = map(int, nums)
    radix = sum(nums) - 1
    return radix


def get_dragonfly_radix(shape_str):
    """
    This works for dragonfly shapes formatted as
    R:P:H:A, where R is the already calculated radix
    so grep it and return
    :param shape_str: R:P:H:A
    :return: radix
    """
    radix = int(shape_str.split(":")[0])
    return radix


def cal_torus_radix(shape_str):
    """
    return radix for a given shape of a Torus network
    :param shape_str: formatted as "4x4x4"
    :return: radix, assuming width is 1 all the time
    """
    dim = shape_str.count("x")
    radix = 2 * dim
    return radix


def calculate_radix(df):
    if df["topo"] == "dragonfly":
        df["radix"] = df[df["topo"] == "dragonfly"]["shape"].map(get_dragonfly_radix)
    elif df["topo"] == "torus":
        df["radix"] = df[df["topo"].str.contains("torus")]["shape"].map(cal_torus_radix)
    elif df["topo"] == "fattree":
        pass
    elif df["topo"] == "diameter2":
        pass
    elif df["topo"] == "fishlite" or df["topo"] == "fishnet":
        pass


def plot_everything(df,
                    x_labels,
                    y_labels,
                    plot_class_keys,
                    line_class_keys,
                    output_dir_base,
                    ):
    """
    plot everything from a DataFrame based on various keys given
    :param df: pandas.DataFrame
    :param x_labels: list, labels to be plotted on x-axis
    :param y_labels: list, labels to be plotted on y-axis
    :param plot_class_keys: list, keys that will be used to divide df into groups,
                            each group represents the data to be plotted on a graph
    :param line_class_keys: list, keys that will be used to divide df into groups,
                            each group represents the data to be plotted as a line
    :param output_dir_base: output directory, but this function will also created
                            subdirectories based on x_labels and y_labels
    :return:
    """
    plot_groups = df.groupby(plot_class_keys)
    plot_cnt = 0
    for x_label in x_labels:
        for y_label in y_labels:
            # each of this group should be in a separate plot
            for plot_keys, each_plot_group in plot_groups:
                print plot_keys[0]
                # if needed, add sub_plot groups, but let's not do it now...
                fig, ax = plt.subplots(1, 1)
                line_groups = each_plot_group.groupby(line_class_keys)
                line_cnt = 0
                labels = []
                # each of this group should be a line in plot
                for line_keys, each_line_group in line_groups:
                    group = each_line_group.sort_values(x_label)
                    topo = group[line_keys].iloc[0]
                    labels.append(topo)
                    if not all(group[y_label] == -1):
                        ax.plot(group[x_label], group[y_label],
                                linewidth=2, marker=markers[line_cnt], markersize=8)
                    line_cnt += 1
                title_text = ""
                key_cnt = 0
                for key in plot_class_keys:
                    title_text += "%s=%s_" % (key, str(plot_keys[key_cnt]))
                    key_cnt += 1
                ax.set_title(title_text)
                ax.legend(labels, loc="best")
                ax.set_xlabel(x_label)
                ax.set_ylabel(y_label)
                sub_dir_name = utils.replace_special_char(y_label) + "_vs_" + \
                    utils.replace_special_char(x_label)
                output_dir = os.path.join(output_dir_base, sub_dir_name)
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)
                output_name = "plot_%d.png" % plot_cnt
                output_name = os.path.join(output_dir, output_name)
                plot_cnt += 1
                fig.savefig(output_name, format="png")
                fig.clf()
                plt.close(fig)

pd.DataFrame.mask = mask
plt.style.use('ggplot')


