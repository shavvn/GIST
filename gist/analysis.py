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


def cal_torus_nodes(shape_str, local_ports=1):
    """
    calculate num of nodes in a torus network
    :param shape_str: torus shape string, formatted like axbxcxd... each
        is the number of routers on 1 dimension
    :param local_ports: number of nodes attached on each router, default 1
    :return: num of nodes
    """
    dims = [int(x) for x in shape_str.split("x")]
    num_nodes = local_ports
    print num_nodes
    for x in dims:
        print x
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
        p:h:a
        p is num of hosts per router
        h is intergroup links per router
        a is num of routers per group
        this is the "max" dragonfly setup so num of groups = a*h + 1
        num of nodes is thus (a*h + 1)*a*p
    :return: num of nodes
    """
    shapes = [int(x) for x in shape_str.split(":")]
    if len(shapes) == 3:
        hosts, inter_links, rtrs_per_grp = shapes
    elif len(shapes) == 4:
        radix, hosts, inter_links, rtrs_per_grp = shapes
    else:
        exit("dragonfly shape not right...")
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
        exit("cannot calculate radix due to lack of shape and topo!")
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
    # sanity check to make sure inputs are valid
    res_cols = [col for col in result_cols if col in df]
    plotable_cols = find_multi_val_cols(df, ignore_index_col=True,
                                        exception_cols=(res_cols + ignored_cols))
    graph_params = {}
    for y_col in res_cols:
        for x_col in plotable_cols:
            sub_dir_name = utils.replace_special_char(y_col)
            sub_dir_name += "_vs_"
            sub_dir_name += utils.replace_special_char(x_col)
            graph_params[sub_dir_name] = []
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
                            output_name += "_%d" % g_cnt
                            param["title"] = title
                            param["legends"] = labels
                            param["x"] = x_vals
                            param["y"] = y_vals
                            param["x_label"] = x_col
                            param["y_label"] = y_col
                            param["save_name"] = output_name
                            graph_params[sub_dir_name].append(param)
                            g_cnt += 1
                        else:
                            pass
                    else:
                        pass
    return graph_params


pd.DataFrame.mask = mask


