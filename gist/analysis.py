import itertools

import pandas as pd
from gist import utils


def mask(df, key, value):
    return df[df[key] == value]

pd.DataFrame.mask = mask


def normalize_to_one(series):
    """
    given a series of data, find the max among them and use it as 1
    :param series: input series
    :return: new series with a max of 1
    """
    s_max = series.max()
    new_series = series / s_max
    return new_series


def filter_key_val(df, **kwargs):
    """
    this will filter df based on a key: value pair
    :param df:
    :param key_val_dict:
    :return:
    """
    new_df = df.copy(deep=True)
    for key, val in kwargs:
        new_df = new_df.mask(key, val)
    return new_df


def filter_key_vals(df, **kwargs):
    """
    this will filter df based on key:[vals]
    :param df:
    :param kwargs:
    :return:
    """
    new_df = df.copy(deep=True)
    for key, vals in kwargs:
        assert isinstance(vals, list)
        new_df = new_df[key].isin(vals)
    return new_df


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





