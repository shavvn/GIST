import itertools
import numpy as np
import pandas as pd
from gist import utils


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
            if bw_rows.any():
                new_df[col].replace(regex=True, inplace=True,
                                    to_replace=r'\D', value=r'')

                new_df[col] = new_df[col].map(float)

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
    This works for dragonfly shapes formatted as R:P:H:A,
    where R is the already calculated radix so grep it and return
    Or if the input shape is old fashion "PxHxA" then actually calculate it
    :param shape_str: R:P:H:A,
        R=Radix, P=Local Ports, H=Intergroup Links A=Routers per group
    :return: radix
    """
    if "x" in shape_str:
        nums = shape_str.split("x")
        nums = map(int, nums)
        radix = sum(nums) - 1
        return radix
    else:
        radix = int(shape_str.split(":")[0])
        return radix


def cal_torus_radix(shape_str):
    """
    return radix for a given shape of a Torus network
    :param shape_str: formatted as "4x4x4:1:1", which is
        dims:local_port:width. If an old fashion "axbxc" format
        is passed into this then assume local and width are all 1
    :return: radix, assuming
    """
    try:
        shape, local, width = shape_str.split(":")
    except ValueError:
        local = 1
        width = 1
        shape = shape_str
    local = int(local)
    width = int(width)
    dim = shape.count("x") + 1
    radix = 2 * dim * width + local
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
        radix = cal_dragonfly_radix(shape)
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


def add_radix_col(df):
    """
    add a radix column to df, calculated based on "topo" and "shape" cols
    :param df: input df, must contain "topo" and "shape" cols
    :return: a new df with a "radix" column
    """
    if "topo" in df and "shape" in df:
        new_df = df.copy()
        new_df["radix"] = new_df.apply(lambda x: calculate_radix(x["topo"], x["shape"]),
                                       axis=1)
        return new_df
    else:
        exit("cannot calculate radix due to lack of shape and topo!")


def add_radix_col_by_loop(df):
    """
    This is much much slower than add_radix_col
    just acting as an example, should not be used at all
    :param df:
    :return:
    """
    if "topo" in df and "shape" in df:
        new_df = df.copy()
        for index, row in new_df.iterrows():
            new_df.loc[index, "radix"] = calculate_radix(row["topo"], row["shape"])
        return new_df
    else:
        exit("cannot calculate radix due to lack of shape and topo!")


def cal_torus_nodes(shape_str):
    """
    calculate num of nodes in a torus network
    :param shape_str: formatted as "4x4x4:1:1", which is
        dims:local_port:width. If an old fashion "axbxc" format
        is passed into this then assume local and width are all 1
    :param local_ports: number of nodes attached on each router, default 1
    :return: num of nodes
    """
    try:
        shape, local, width = shape_str.split(":")
    except ValueError:
        local = 1
        width = 1
        shape = shape_str
    local = int(local)
    dims = [int(x) for x in shape.split("x")]
    num_nodes = local
    for x in dims:
        num_nodes *= x
    return num_nodes


def cal_fattree_nodes(shape_str):
    """
    calculate num of nodes in fattree shape string
    :param shape_str: a fattree shape str is formatted as follows:
        a,a:b,b:...c
        different levels are separated by ":", ups and down links in
        each level is separated by ","
        num of nodes is calculated by multiplying downs
    :return: num of nodes
    """
    levels = shape_str.split(":")
    downs = []
    for l in levels:
        links = l.split(",")
        downs.append(int(links[0]))
    nodes = 1
    for x in downs:
        nodes *= x
    return nodes


def cal_dragonfly_nodes(shape_str):
    """
    calculate num of nodes in a dragonfly shape string
    :param shape_str: a dragonfly shape str is formatted as follows:
        r:p:h:a
        r is radix, optional
        p is num of hosts per router
        h is intergroup links per router
        a is num of routers per group
        this is the "max" dragonfly setup so num of groups = a*h + 1
        num of nodes is thus (a*h + 1)*a*p
    :return: num of nodes
    """
    if "x" in shape_str:  # might be old fashion "PxHxA"
        shapes = [int(x) for x in shape_str.split("x")]
        if len(shapes) != 3:
            print ("dragonfly shape invalid...%s" % shape_str)
            return
    else:
        shapes = [int(x) for x in shape_str.split(":")]
    if len(shapes) == 3:
        hosts, inter_links, rtrs_per_grp = shapes
    elif len(shapes) == 4:
        radix, hosts, inter_links, rtrs_per_grp = shapes
    else:
        print ("dragonfly shape invalid...%s" % shape_str)
        return
    num_grps = inter_links * rtrs_per_grp + 1
    nodes = hosts * rtrs_per_grp * num_grps
    return nodes


def cal_dia2_nodes(shape_str):
    """
    calculate num of nodes in a diameter 2 shape str by a table lookup
    :param shape_str: formatted as "radix:hosts"
        num of routers is determined by radix, and multiplied by
        num of hosts is num of nodes
    :return: num of nodes
    """
    mapping = {
        "5": 18,
        "7": 50,
        "11": 98,
        "17": 242,
        "19": 338,
        "25": 578,
        "29": 722,
        "35": 1058,
        "43": 1682,
        "47": 1922,
        "55": 2738,
        "79": 5618
    }
    radix, hosts = shape_str.split(":")
    nodes = mapping[radix] * int(hosts)
    return nodes


def cal_fish_nodes(shape_str):
    """
    calculate fishnet/fishlite nodes, based on dia2 graphs
    :param shape_str: same as dia2
    :return: num of nodes
    """
    nodes = cal_dia2_nodes(shape_str)
    nodes *= (nodes + 1)
    return nodes


def cal_num_nodes(topo, shape):
    nodes = 0
    if topo == "dragonfly":
        nodes = cal_dragonfly_nodes(shape)
    elif "torus" in topo:
        nodes = cal_torus_nodes(shape)
    elif "fattree" in topo:
        nodes = cal_fattree_nodes(shape)
    elif "diameter2" in topo:
        nodes = cal_dia2_nodes(shape)
    elif "fishlite" in topo:
        nodes = cal_fish_nodes(shape)
    elif "fishnet" in topo:
        nodes = cal_fish_nodes(shape)
    return nodes


def add_num_nodes_col(df):
    """
    add a column of num of nodes to a df, based on "topo", "shape" cols, and
    potentially other cols e.g. "torus:local_ports"
    :param df: input df, must contain "topo" and "shape" cols
    :return:a new df with a "num_nodes" column
    """
    if "topo" in df and "shape" in df:
        new_df = df.copy()
        new_df["num_nodes"] = new_df.apply(lambda x: cal_num_nodes(x["topo"],
                                                                   x["shape"]),
                                           axis=1)
        return new_df
    else:
        exit("cannot calculate num_nodes due to lack of shape and topo!")
    return df


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
    elif pd_obj.count() < 2:
        # count() here also eliminate those series with only 1 valid data point
        # while all others are np.nan
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
                x_vals.append(line[x_col].tolist())
                y_vals.append(line[y_col].tolist())
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
    :param keys: list of keys
    :param vals: list of vals
    :return: str like "key0=val0key1=val1..."
    """
    title_text = ""
    for key, val in zip(keys, vals):
        title_text += "%s=%s" % (str(key), str(val))
    return title_text


def get_plotable_data(df, result_cols, ignored_cols=None):
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
    :return: a dict of keys as sub classes and values are lists of params that
        could be used to plot graphs
    """
    # sanity check to make sure inputs are valid
    res_cols = [col for col in result_cols if col in df]
    plotable_cols = find_multi_val_cols(df, ignore_index_col=True,
                                        exception_cols=(res_cols + ignored_cols))
    graph_params = {}

    # maintain a counter for each sub_dir
    g_counters = {}

    for x_col, line_col in itertools.permutations(plotable_cols, r=2):
        other_cols = [x for x in plotable_cols if x not in [x_col, line_col]]
        groups = df.groupby(other_cols)
        for index_vals, group in groups:
            for y_col in res_cols:

                sub_dir_name = utils.replace_special_char(y_col)
                sub_dir_name += "_vs_"
                sub_dir_name += utils.replace_special_char(x_col)

                if sub_dir_name not in graph_params:
                    graph_params[sub_dir_name] = []
                    g_counters[sub_dir_name] = 0

                if _pd_data_valid(group[x_col]) and \
                   _pd_data_valid(group[y_col]) and \
                   _pd_data_valid(group[line_col]):
                    sorted_group = group.sort_values(by=x_col, ascending=False)
                    lines = sorted_group.groupby(line_col)
                    labels = _get_labels_from_groups(lines, line_col)
                    x_vals, y_vals = _get_x_y_from_groups(lines, x_col, y_col)

                    if x_vals and y_vals:
                        params = {}
                        title = _get_title_text(other_cols, index_vals)
                        output_name = utils.replace_special_char(line_col)
                        output_name += "_%d" % g_counters[sub_dir_name]
                        params["title"] = title
                        params["legends"] = labels
                        params["x"] = x_vals
                        params["y"] = y_vals
                        params["x_label"] = x_col
                        params["y_label"] = y_col
                        params["save_name"] = output_name
                        graph_params[sub_dir_name].append(params)
                        g_counters[sub_dir_name] += 1
    return graph_params


def get_plotable_data_3d(df, result_cols, ignored_cols=None):
    """
    this so far is dedicated for 3D bars...
    :param df:
    :param result_cols:
    :param ignored_cols:
    :return:
    """
    # sanity check on result_cols
    res_cols = [col for col in result_cols if col in df]
    plotable_cols = find_multi_val_cols(df, ignore_index_col=True,
                                        exception_cols=(res_cols + ignored_cols))
    graph_params = {}
    for z_col in res_cols:
        for x_col, y_col in itertools.combinations(plotable_cols, 2):
            sub_dir_name = utils.replace_special_char(z_col)
            sub_dir_name += "_vs_"
            sub_dir_name += utils.replace_special_char(y_col)
            sub_dir_name += "_vs_"
            sub_dir_name += utils.replace_special_char(x_col)
            graph_params[sub_dir_name] = []
            other_cols = [t for t in plotable_cols if t not in [x_col, y_col]]
            graph_groups = df.groupby(other_cols)
            for vals, graph_group in graph_groups:
                params = {}
                if _pd_data_valid(graph_group[z_col]) and \
                   _pd_data_valid(graph_group[y_col]) and \
                   _pd_data_valid(graph_group[x_col]):
                    sorted_graph = graph_group.sort_values(by=[x_col, y_col],
                                                           ascending=True)
                    x_vals = sorted_graph[x_col].unique()
                    y_vals = sorted_graph[y_col].unique()
                    # note the order of z is sorted by [x, y]
                    z_vals = sorted_graph[z_col]
                    params["x"] = x_vals
                    params["y"] = y_vals
                    params["z"] = z_vals
                    title = _get_title_text(other_cols, vals)
                    params["title"] = title
                    params["x_label"] = x_col
                    params["y_label"] = y_col
                    params["z_label"] = z_col
                    params["save_name"] = title
                    graph_params[sub_dir_name].append(params)
    return graph_params


pd.DataFrame.mask = mask


