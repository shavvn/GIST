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
            df.ix[(df["topo"] == "torus") &
                  (df["shape"].str.count("x") == x),
                  "topo"] = "torus_%d" % (x + 1)
    colon_s = df["shape"].str.count(":").unique()
    for x in colon_s:
        if x > 0:
            df.ix[(df["topo"] == "fattree") &
                  (df["shape"].str.count(":") == x),
                  "topo"] = "fattree_%d" % (x + 1)
    return df


def move_bw_unit_to_index(df):
    col_replace_pairs = {}
    for col in df:
        gbs_rows = df[col].str.contains("GB/s")
        df[gbs_rows][col].replace(regex=True, inplace=True,
                                  to_replace=r'\D', value=r'')
        # maybe do MB/s KB/s later?
        col_replace_pairs.update({col:col+"(GB/s)"})
    df.rename(columns=col_replace_pairs, inplace=True)
    return df


def move_units_to_index(df):
    """
    This function should be part of pre-processing before plotting
    this moves
    e.g. from "bw": ["1GB/s", "2GB/s"] to "bw(GB/s)": [1, 2]
    NOTE this should be done before replacing NaN with -1
    :param df: input df that may have units in its values
    :return: a df that has all units moved to col
    """
    # df ranaming http://stackoverflow.com/questions/11346283/renaming-columns-in-pandas
    # then use set_value method
    cols = df.columns
    # TODO should check different types of units and unify them
    # e.g. "MB" to "GB", "ns" to "us" etc.
    # this should work like calculate_radix function
    for col in df:
        gbs_rows = df[col].str.contains("GB/s")
        df[gbs_rows][col].replace(regex=True, inplace=True,
                                  to_replace=r'\D', value=r'')


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
    radix = 2 * (dim + 1)
    return radix


def cal_fattree_radix(shape_str):
    """
    radix for fattree is different from others since the radix
    of each router might be different, so only return the max
    here?
    :param shape_str: formatted as "2,2:4,4:8"
    :return: max radix of the routers
    """
    levels = shape_str.split(":")
    max_radix = 0
    for l in levels:
        radix = sum(map(int, l.split(",")))
        if radix > max_radix:
            max_radix = radix
    return max_radix


def cal_dia2_radix(shape_str):
    """
    for diameter2 graphs shape is simply the local ports: host ports
    :param shape_str: formatted as "local:host"
    :return: radix
    """
    local, host = map(int, shape_str.split(":"))
    radix = local + host
    return radix


def cal_fishlite_radix(shape_str):
    """
    for fishlite graphs radix is simply the local ports + host ports + 1
    :param shape_str: formatted as "local:host"
    :return: radix
    """
    local, host = map(int, shape_str.split(":"))
    radix = local + host + 1
    return radix


def cal_fishnet_radix(shape_str):
    """
    for fishnet graphs radix is simply the local ports*2 + host ports
    :param shape_str: formatted as "local:host"
    :return: radix
    """
    local, host = map(int, shape_str.split(":"))
    radix = local * 2 + host
    return radix


def calculate_radix(topo, shape):
    """
    given a topo and shape, calculate radix using the sub-functions
    above, to use this function with DataFrame object, do:
    df["radix"] = df.apply(lambda x: \
    analysis.calculate_radix(x["topo"], x["shape"]), axis=1)
    :param topo: topology str
    :param shape: shape str
    :return: radix, 0 if cannot recognize
    """
    radix = 0
    if topo == "dragonfly":
        radix = get_dragonfly_radix(shape)
    elif "torus" in topo:
        radix = cal_torus_radix(shape)
    elif "fattree" in topo:
        radix = cal_fattree_radix(shape)
    elif "diameter2" in topo:
        radix = cal_dia2_radix(shape)
    elif "fishlite" in topo:
        radix = cal_fishlite_radix(shape)
    elif "fishnet" in topo:
        radix = cal_fishnet_radix(shape)
    return radix


def concat_summarys(file_list, output_name="super_summary.csv"):
    """
    concatenate output summaries from various places
    and thanks to pandas the header and index will be handled
    :param file_list: list of file paths or pointers to summary csv files
    :param output_name: output csv file name
    :return: None
    """
    frames = []
    for csv in file_list:
        df = pd.read_csv(csv, index_col=0)
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df.to_csv(output_name)


def plot_all_lines(df,
                   x_labels,
                   y_labels,
                   plot_class_keys,
                   line_key,
                   output_dir_base,
                   ):
    """
    plot everything from a DataFrame based on various keys given
    :param df: pandas.DataFrame
    :param x_labels: list, labels to be plotted on x-axis
    :param y_labels: list, labels to be plotted on y-axis
    :param plot_class_keys: list, keys that will be used to divide df into groups,
                            each group represents the data to be plotted on a graph
    :param line_key: str, key that will be used to divide df into groups,
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
                # if needed, add sub_plot groups, but let's not do it now...
                fig, ax = plt.subplots(1, 1)
                line_groups = each_plot_group.groupby(line_key)
                line_cnt = 0
                labels = []
                # each of this group should be a line in plot
                for line_keys, each_line_group in line_groups:
                    group = each_line_group.sort_values(x_label)
                    topo = group.iloc[0][line_key]
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


def find_multi_val_cols(df, ignore_index_col=True, exception_cols=[]):
    """
    find columns that has multiple values from a dataframe
    :param df: input dataframe
    :param ignore_index_col: if this is true then ignore the index col
    (the first col), by default is true
    :param exception_cols: col names will be check against this list,
    those in this list will be ignored and will not be returned
    :return: a list with column names that satisfy above requirements
    """
    multi_val_cols = []
    first_col = ignore_index_col
    for col in df:
        if first_col:
            first_col = False
            continue
        else:
            if col in exception_cols:
                continue
            else:
                if df[col].nunique() > 1:
                    multi_val_cols.append(col)
                else:
                    pass
    return multi_val_cols


def plot_everything_in_lines(df, output_dir_base, result_cols, ignored_cols=[]):
    """
    Plot everything that could be plotted in a dataframe in line graphs
    :param df: input dataframe, assuming the df is properly processed and all
    nan are replaced by -1
    :param output_dir_base: where the graphs will be outputted
    :param result_cols: list of columns in df that are actually results,
    these cols will not be plotted on x-axis
    :param ignored_cols: columns that are ignored
    :return:
    """
    plotable_cols = find_multi_val_cols(df, ignore_index_col=True,
                                        exception_cols=(result_cols+ignored_cols))
    plot_cnt = 0
    for y_col in result_cols:
        for x_col in plotable_cols:
            sub_dir_name = utils.replace_special_char(y_col)
            sub_dir_name += "_vs_"
            sub_dir_name += utils.replace_special_char(x_col)
            output_dir = os.path.join(output_dir_base, sub_dir_name)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            other_cols = [item for item in plotable_cols if item != x_col]
            # There ia a design decision here that whether to plot a lot of
            # stuff on one graph or fewer things on separate graphs
            # use the later one for now
            # plot line_col, groupby other cols
            for line_col in other_cols:
                group_cols = [item for item in other_cols if item != line_col]
                graph_groups = df.groupby(group_cols)
                # each group represent a graph
                for graph_name_vals, line_group in graph_groups:
                    # if either x or y axis are NaN then move on to next graph
                    if all(pd.isnull(line_group[y_col])) or \
                       all(line_group[y_col] == -1):
                        continue
                    elif all(pd.isnull(line_group[x_col])) or \
                         all(line_group[x_col] == -1):
                        continue
                    elif all(pd.isnull(line_group[line_col])) or \
                         all(line_group[line_col] == -1):
                        continue
                    else:
                        lines = line_group.groupby(line_col)
                        labels = []
                        fig, ax = plt.subplots(1, 1)
                        line_cnt = 0
                        for line_name_vals, line in lines:
                            sorted_group = line.sort_values(x_col)
                            label = sorted_group.iloc[0][line_col]
                            labels.append(label)
                            if all(pd.isnull(sorted_group[y_col])):
                                continue
                            elif all(pd.isnull(sorted_group[x_col])):
                                continue
                            else:
                                ax.plot(sorted_group[x_col], sorted_group[y_col],
                                        linewidth=2, marker=markers[line_cnt], markersize=8)
                                line_cnt += 1
                        title_text = ""
                        for key, val in zip(group_cols, graph_name_vals):
                            title_text += "%s=%s" % (str(key), str(val))
                        ax.set_title(title_text)
                        ax.legend(labels, loc="best")
                        ax.set_xlabel(x_col)
                        ax.set_ylabel(y_col)
                        output_name = "%s_%d.png" % (line_col, plot_cnt)
                        output_name = os.path.join(output_dir, output_name)
                        fig.savefig(output_name, format="png")
                        plt.close(fig)
                        plot_cnt += 1


pd.DataFrame.mask = mask
plt.style.use('ggplot')


