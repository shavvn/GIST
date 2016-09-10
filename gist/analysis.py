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
    """
    This is pretty tricky since pandas makes the object copy behavior
    very unpredictable
    :param df: input df, should have no side effect after this func call
    :return: a new copy of df that has bw units moved to col label
    """
    # make a new copy to avoid side effects
    new_df = df.copy()
    col_replace_pairs = {}
    for col in new_df:
        if new_df[col].dtype == 'O':
            bw_rows = new_df[col].str.contains(r'\d+\.*\d*\s*GB/s')
            if not all(bw_rows == False):
                # use .loc to make sure it's operated on original copy (new_df)
                # because the inplace flag doesn't always work as it should, wtf...
                new_df.loc[bw_rows, col] = new_df[bw_rows][col].replace(regex=True, inplace=False,
                                                                        to_replace=r'\D', value=r'')
                new_df.loc[bw_rows, col] = new_df[bw_rows][col].map(lambda x: float(x))
                # maybe do MB/s KB/s as well?
                col_replace_pairs.update({col: col+"(GB/s)"})
    new_df.rename(columns=col_replace_pairs, inplace=True)
    return new_df


def move_units_to_index(df):
    """
    This function should be part of pre-processing before plotting
    this moves
    e.g. from "bw": ["1GB/s", "2GB/s"] to "bw(GB/s)": [1, 2]
    NOTE this should be done before replacing NaN with -1
    :param df: input df that may have units in its values
    :return: a df that has all units moved to col
    """
    move_bw_unit_to_index(df)


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


def _pd_data_valid(pd_obj):
    """
    check if data is valid in a pandas object for *plotting*
    it's not valid if all null or all -1 or only 1 data point
    Note that -1 is the arbitrary value I assigned
    :param pd_obj: pandas object, either DF or Series
    :return: True if valid, False otherwise
    """
    if all(pd.isnull(pd_obj)):
        return False
    elif all(pd_obj == -1):
        return False
    elif len(pd_obj) <= 1:
        return False
    else:
        return True


def _get_x_y_from_groups(data_groups, x_col, y_col):
    """
    :param data_groups: should be a groupby obj, each group represents a line
                        assume it's already sorted
    :param x_col: indexer of column that to be plotted as x
    :param y_col: indexer of column that to be plotted as y
    :return: x_val, y_val, both are lists of lists representing a set of data
    """
    x_vals = []
    y_vals = []
    if not data_groups:
        return x_vals, y_vals
    else:
        for line_name_vals, line in data_groups:
            if _pd_data_valid(line[x_col]) and \
               _pd_data_valid(line[y_col]):
                x_vals.append(line[x_col])
                y_vals.append(line[y_col])
            else:
                pass
    return x_vals, y_vals


def _get_labels_from_groups(data_groups, col_index):
    """
    get data labels from groupby object
    :param data_groups: groupby object, each represent a set of data
    to be plotted
    :param col_index: column index for the label
    :return: a list of labels for data
    """
    labels = []
    for line_name_vals, line in data_groups:
        label = line.iloc[0][col_index]
        labels.append(label)
    return labels


def _get_title_text(keys, vals):
    """
    get graph title text from key, value pairs,
    :param keys:
    :param vals:
    :return:
    """
    title_text = ""
    for key, val in zip(keys, vals):
        title_text += "%s=%s" % (str(key), str(val))
    return title_text


def get_plotable_data(df, result_cols, ignored_cols=[]):
    """
    get plotable data (2D) from a dataframe, you need to specify which ones
    are results and which cols should be ignored. Will return a list of dicts
    that should provide enough info to plot a graph. e.g. x, y vals, labels,
    title, output_dir, output_name, etc.
    :param df: input dataframe
    :param result_cols:list of columns in df that are actually results,
    these cols will not be plotted on x-axis
    :param ignored_cols: columns that are ignored, usually those with variants
    but don't matter
    :return: a list of dicts, each should contain enough data to plot
    """
    plotable_cols = find_multi_val_cols(df, ignore_index_col=True,
                                        exception_cols=(result_cols + ignored_cols))
    graph_params = []
    for y_col in result_cols:
        for x_col in plotable_cols:
            sub_dir_name = utils.replace_special_char(y_col)
            sub_dir_name += "_vs_"
            sub_dir_name += utils.replace_special_char(x_col)
            other_cols = [item for item in plotable_cols if item != x_col]
            # pick one metric to plot different lines while keeping all others same
            for line_col in other_cols:
                group_cols = [item for item in other_cols if item != line_col]
                graph_groups = df.groupby(group_cols)
                # each group represent a graph
                g_cnt = 0
                for graph_name_vals, graph_group in graph_groups:
                    param = {}
                    if _pd_data_valid(graph_group[y_col]) and \
                       _pd_data_valid(graph_group[x_col]) and \
                       _pd_data_valid(graph_group[line_col]):
                        sorted_graph = graph_group.sort_values(by=x_col,
                                                               ascending=True)
                        lines = sorted_graph.groupby(line_col)
                        labels = _get_labels_from_groups(lines, line_col)
                        x_vals, y_vals = _get_x_y_from_groups(lines, x_col, y_col)
                        if x_vals and y_vals:
                            title = _get_title_text(group_cols, graph_name_vals)
                            output_name = utils.replace_special_char(line_col)
                            output_name += str(g_cnt)
                            param["title"] = title
                            param["legends"] = labels
                            param["x"] = x_vals
                            param["y"] = y_vals
                            param["x_label"] = x_col
                            param["y_label"] = y_col
                            param["save_dir"] = sub_dir_name
                            param["save_name"] = output_name
                            graph_params.append(param)
                            g_cnt += 1
                        else:
                            pass
                    else:
                        pass
    return graph_params


pd.DataFrame.mask = mask
plt.style.use('ggplot')


