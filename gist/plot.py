import os
import matplotlib.pyplot as plt

"""
this file will eventually look like the polly project I did a while back...
TODO move all plotting stuff from analysis to here
"""

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


def lines(params, fig_format="png", output_dir="."):
    """
    plot lines from a param dict, maybe should define it more strictly..
    :param params: should have following keys:
        {
            "title": # title of graph,
            "legends": # legends for multiple lines,
            "x_label": # x axis label,
            "y_label": # y axis label,
            "x": # x data,
            "y": # y data,
            "save_dir": # RELATIVE dir where fig will be saved
            "save_name": # save file name
        }
    :param fig_format: figure format, "png" or "pdf
    :param output_dir: directory  where figs will be saved
    :return: none for now
    """
    fig, ax = plt.subplots(1, 1)
    cnt = 0
    for x, y in zip(params["x"], params["y"]):
        # maybe do sanity check for x y
        ax.plot(x, y, linewidth=2, marker=markers[cnt], markersize=8)
        cnt += 1
    ax.set_title(params["title"])
    ax.legend(params["legends"], loc="best")
    ax.set_xlabel(params["x_label"])
    ax.set_ylabel(params["y_label"])
    ax.set_xlim(0)
    ax.set_ylim(0)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    output_name = os.path.join(output_dir, params["save_name"])
    if fig_format == "png":
        output_name += ".png"
    elif fig_format == "pdf":
        output_name += ".pdf"
    else:
        exit("invalid output format!")
    fig.savefig(output_name, format=fig_format)
    plt.close(fig)

