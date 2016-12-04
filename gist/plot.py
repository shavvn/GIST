import os
import numpy as np
import matplotlib.pyplot as plt

"""
this file will eventually look like the polly project I did a while back...
"""

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


hatches = ["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]


class Colors(object):

    def __init__(self, scheme="colorful", ncolors=0):
        self.colors = []
        self.type = "colorful"
        self.counter = 0
        if scheme == "colorful":
            colors = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
                      (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
                      (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
                      (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
                      (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

            for c in range(len(colors)):
                r, g, b = colors[c]
                colors[c] = (r / 255., g / 255., b / 255.)

            self.colors = colors
            self.type = scheme
        elif scheme == "bw" or scheme == "grey":
            if ncolors == 0:
                print "number of colors has to be specified for gray/bw colors"
            else:
                inc = 248/ncolors  # to very light gray instead of white (256)
                colors = [c/255. for c in range(0, 248, inc)]

                self.colors = colors
                self.type = "bw"
        else:
            pass

    def __len__(self):
        return len(self.colors)

    def __getitem__(self, item):
        return self.colors[item]

    def next(self):
        next_color = self.colors[self.counter]
        self.counter += 1
        if self.counter == self.__len__():
            self.counter = 0
        return next_color


class Markers(object):

    def __init__(self):
        self.markers = {  # this is a copy from matplotlib.markers.py ...
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

        self.counter = 0

    def __len__(self):
        return len(self.markers)

    def __getitem__(self, item):
        return self.markers[item]

    def next(self):
        next_marker = self.markers[self.counter]
        self.counter += 1
        if self.counter == self.__len__():
            self.counter = 0
        return next_marker


class Axes2D(object):
    def __init__(self, axes, **kwargs):
        self.ax = axes
        self.params = {
            "title": "Default Title",
            "xlabel": "X Axis",
            "xticks": None,
            "ylabel": "Y Axis",
            "yticks": None,
            "color_scheme": "colorful",
            "legends": False
        }
        self.set_params(**kwargs)
        self.colors = Colors(self.params["color_scheme"])
        self.markers = Markers()

    def set_params(self, **kwargs):
        self.params.update(kwargs)

    def set_title(self, max_len=40):
        """
        if title text is too long, split it into max_len chunks and
        :param max_len: max num of chars per line
        :return:
        """
        title_text = self.params["title"]
        chunks = [title_text[i:i+max_len] for i in range(0, len(title_text), max_len)]
        new_title = ""
        for c in chunks:
            new_title += (c + os.linesep)
        self.ax.set_title(new_title)

    def set_x_axis(self):
        self.ax.xaxis.set_label_position('bottom')
        self.ax.xaxis.set_ticks_position('bottom')
        self.ax.set_xlabel(self.params["xlabel"])
        ticks = self.params["xticks"]
        if not ticks:
            pass
        else:
            ticks = range(len(ticks))
            self.ax.set_xticks(ticks)
            self.ax.set_xticklabels(ticks, ha="center")

        self.ax.set_xlim(0)

    def set_y_axis(self):
        self.ax.set_ylabel(self.params["ylabel"])
        self.ax.set_ylim(0)

    def set_legend(self):
        if self.params["legends"]:
            self.ax.legend(self.params["legends"], loc="best")
        else:
            return


class Scatter(Axes2D):

    def __init__(self, axes, **kwargs):
        super(Scatter, self).__init__(axes, **kwargs)

        assert "x" in self.params
        assert "y" in self.params

        if not (self.params["x"] and self.params["y"]):
            exit("Input data x and y must be specified!")

        self.plot()

    def plot(self):
        assert len(self.params["x"]) == len(self.params["y"])
        assert type(self.params["x"]) == type(self.params["y"])
        for x, y in zip(self.params["x"], self.params["y"]):
            self.ax.scatter(x,
                            y,
                            color=next(self.colors),
                            marker=next(self.markers),
                            s=20
                            )
        self.set_legend()


class GroupedBar(Axes2D):
    def __init__(self, axes, **kwargs):
        super(GroupedBar, self).__init__(axes, **kwargs)

        assert "x" in self.params
        assert "y" in self.params

        self.plot()

    def plot(self):
        x = self.params["x"]
        y = self.params["y"]
        for each_y in y:
            assert len(each_y) == len(x)
        num_bars_per_group = len(y)
        num_groups = len(x)
        bar_width = 1./(num_bars_per_group+1)
        x_pos = np.arange(num_groups, dtype=np.float)

        for each_y in y:
            self.ax.bar(x_pos,
                        height=each_y,
                        width=bar_width,
                        color=next(self.colors))
            x_pos += bar_width

        self.set_title()
        # self.set_x_axis()
        x_ticks = np.arange(num_groups, dtype=np.float) + 0.5
        x_ticklabels = map(str, x)

        self.set_xaxis(x_ticks, x_ticklabels, self.params["xlabel"])
        self.set_y_axis()
        self.set_legend()

    def set_xaxis(self, x_ticks, x_ticklabels, x_label):
        self.ax.set_xlabel(self.params["xlabel"])
        self.ax.set_xticks(x_ticks)
        self.ax.set_xticklabels(x_ticklabels)


class Bar(Axes2D):

    def __init__(self, axes, **kwargs):
        super(Bar, self).__init__(axes, **kwargs)

        assert "x" in self.params
        assert "y" in self.params

        if not (self.params["x"] and self.params["y"]):
            exit("Input data x and y must be specified!")

        self.plot()

    def plot(self):
        """
        data in the following format
        [[group_1_x_1, group_2_x_1, group_3_x_1 ... ], [group_1_x_2, group_2_x_2, ...]]
        :return: False if failed to plot, ax obj otherwise
        """

        if len(params["x"]) == 0:
            return False
        if len(params["x"][0]) <= 1:
            return False
        else:
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
                _ticks = map(lambda x: x * dist, _ticks)
                x_pos = [x + offset for x in _ticks]
                self.ax.bar(x_pos, height=y, width=bar_width, color=colors[cnt])
                offset += bar_width
                cnt += 1
            # scale x_ticks for grouped bars and then move to center a little
            x_ticks = [x * dist for x in x_ticks]
            x_ticks = [x + bar_width for x in x_ticks]
            self.ax.set_xticks(x_ticks)
            self.ax.set_xticklabels(x_ticklabels, ha="center", rotation=45)
            self.set_title()
            self.ax.legend(params["legends"], loc="best")
            self.ax.set_xlabel(params["x_label"])
            self.ax.set_ylabel(params["y_label"])
            return self.ax


# color scheme courtesy to
# http://www.randalolson.com/2014/06/28/\
# how-to-make-beautiful-data-visualizations-in-python-with-matplotlib/

colors = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
          (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
          (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
          (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
          (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.
for c in range(len(colors)):
    r, g, b = colors[c]
    colors[c] = (r / 255., g / 255., b / 255.)


def _set_title(ax, title_text, max_len=60):
    """
    this function handles the situations where title gets too long
    and got cut off at the edge of the graph. this will fold the title
    into multiple lines and then call ax.set_title() function
    :param ax: matplotlib axes handle
    :param title_text: title text
    :param max_len: max line length the lines will be broken into
    :return: same axes object
    """
    multi_lines = len(title_text) / max_len
    if multi_lines == 0:
        ax.set_title(title_text)
    else:
        new_title = ""
        for i in range(multi_lines):
            front = i * max_len
            end = (i + 1) * max_len
            new_title += (title_text[front:end] + os.linesep)
        new_title += title_text[multi_lines * max_len:]
        ax.set_title(new_title)
    return ax


def save_fig(fig, out_dir, name, fig_format):
    """
    save a figure
    :param fig: matplotlib fig handler
    :param out_dir: output dir, will be created if not exists
    :param name: output name, could contain suffix ".png" or ".pdf" or not
    :param fig_format: "png" and "pdf" only
    :return: same fig handler
    """
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    output_name = os.path.join(out_dir, name)
    if ".%s" % fig_format in name:
        pass
    else:
        if fig_format == "png":
            output_name += ".png"
        elif fig_format == "pdf":
            output_name += ".pdf"
        else:
            exit("invalid output format!")
    fig.savefig(output_name, format=fig_format)
    return fig


def lines_save(params, fig_format="png", output_dir="."):
    """
    plot line graph and then save, plot based on params, save in
    designated dir and format, close fig when done.
    :param params: graph params, see lines() for more detail
    :param fig_format: figure format, "png" or "pdf
    :param output_dir: directory  where figs will be saved
    :return: none for now
    """
    fig, ax = plt.subplots(1, 1)
    if not lines(ax, params):
        print "failed to plot scatter graph!"
        plt.close(fig)
        return False
    fig = save_fig(fig, output_dir, params["save_name"], fig_format)
    plt.close(fig)


def lines(ax, params):
    """
    plot lines from a param dict
    :param ax: matplotlib axes obj
    :param params: dict, should have following keys:
        {
            "title": # title of graph,
            "legends": # legends for multiple lines,
            "x_label": # x axis label,
            "y_label": # y axis label,
            "x": # x data,
            "y": # y data,
            "save_name": # save file name
        }
    :return: False if failed to plot, ax obj otherwise
    """
    cnt = 0
    for x, y in zip(params["x"], params["y"]):
        # maybe do sanity check for x y
        ax.plot(x, y, linewidth=2, marker=markers[cnt], markersize=8)
        cnt += 1
    ax = _set_title(ax, params["title"])
    ax.legend(params["legends"], loc="best")
    ax.set_xlabel(params["x_label"])
    ax.set_ylabel(params["y_label"])
    ax.set_xlim(0)
    ax.set_ylim(0)
    return ax


def bars_save(params, fig_format="png", output_dir="."):
    """
    plot bar graph and then save, plot based on params, save in
    designated dir and format, close fig when done.
    :param params: graph params, see bars() for more detail
    :param fig_format: figure format, "png" or "pdf
    :param output_dir: directory  where figs will be saved
    :return: none for now
    """
    fig, ax = plt.subplots(1, 1)
    if not bars(ax, params):
        print "failed to plot scatter graph!"
        plt.close(fig)
        return False
    fig = save_fig(fig, output_dir, params["save_name"], fig_format)
    plt.close(fig)


def bars(ax, params):
    """
    plot bars from params dict
    :param ax: matplotlib axes obj
    :param params: dict, should have the following keys
        {
            "title": # title of graph,
            "legends": # legends for multiple lines,
            "x_label": # x axis label,
            "y_label": # y axis label,
            "x": # x data,
            "y": # y data,
            "save_name": # save file name
        }
    :return: False if failed to plot, ax obj otherwise
    """
    if len(params["x"]) == 0:
        return False
    if len(params["x"][0]) <= 1:
        return False
    else:
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
        # scale x_ticks for grouped bars and then move to center a little
        x_ticks = [x * dist for x in x_ticks]
        x_ticks = [x + bar_width for x in x_ticks]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_ticklabels, ha="center", rotation=45)
        ax = _set_title(ax, params["title"])
        ax.legend(params["legends"], loc="best")
        ax.set_xlabel(params["x_label"])
        ax.set_ylabel(params["y_label"])
        return ax


def bars_3d(params, fig_format="png", output_dir="."):
    """
    :param params:
    :param fig_format:
    :param output_dir:
    :return:
    """
    return


def scatter_save(params, fig_format="png", output_dir="."):
    """
    plot scatter graph and then save, plot based on params, save in
    designated dir and format, close fig when done.
    :param params: graph params, see scatter() for more detail
    :param fig_format: figure format, "png" or "pdf
    :param output_dir: directory  where figs will be saved
    :return:
    """
    fig, ax = plt.subplots(1, 1)
    if not scatter(ax, params):
        print "failed to plot scatter graph!"
        return False
    fig = save_fig(fig, output_dir, params["save_name"], fig_format)
    plt.close(fig)


def scatter(ax, params):
    """
    plot a scatter graph to axes based on params
    :param ax: matplotlib axes objects
    :param params: dict, should have the following keys
        {
            "title": # title of graph,
            "legends": # legends for multiple groups of points,
            "x_label": # x axis label,
            "y_label": # y axis label,
            "x": # x data, could be 2D list, inner list represents
                 # a group of points
            "y": # y data,
            "save_name": # save file name
        }
    TODO the thing is how to determine the data structure, should
    it be structured so that it's easy to label(legend) or just be
    plain simple...
    :return: False if failed to plot, ax obj otherwise
    """
    return ax

