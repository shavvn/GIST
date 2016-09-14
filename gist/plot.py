import os
import matplotlib.pyplot as plt

"""
this file will eventually look like the polly project I did a while back...
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


hatches = ["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]


# color scheme credit to
# http://www.randalolson.com/2014/06/28/\
# how-to-make-beautiful-data-visualizations-in-python-with-matplotlib/

colors = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
          (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
          (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
          (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
          (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
for i in range(len(colors)):
    r, g, b = colors[i]
    colors[i] = (r / 255., g / 255., b / 255.)


plt.style.use('ggplot')


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


def bars(params, fig_format="png", output_dir="."):
    if len(params["x"]) == 0:
        return
    else:
        fig, ax = plt.subplots(1, 1)
        x_ticks = []
        x_ticklabels = []
        tick = 0
        for x in params["x"]:
            for x_label in x:
                if x_label not in x_ticklabels:
                    x_ticklabels.append(x_label)
                    x_ticks.append(tick)
                    tick += 1
        bars_cnt = len(params["legends"])  # should = len(params["x])
        # 4 bars share 1 unit (cm)
        dist = bars_cnt / 4 + 1
        bar_width = float(1.0) / float(bars_cnt + 1)
        offset = 0.0
        cnt = 0
        for x_labels, y in zip(params["x"], params["y"]):
            _ticks = [x_ticklabels.index(x_label) for x_label in x_labels]
            _ticks = map(lambda x: x*dist, _ticks)
            x_pos = [x + offset for x in _ticks]
            ax.bar(x_pos, height=y, width=bar_width, color=colors[cnt])
            offset += bar_width
            cnt += 1
        x_ticks = [x * dist for x in x_ticks]
        x_ticks = [x + bar_width for x in x_ticks]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_ticklabels, ha="center", rotation=45)
        ax.set_title(params["title"])
        ax.legend(params["legends"], loc="best")
        ax.set_xlabel(params["x_label"])
        ax.set_ylabel(params["y_label"])
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

