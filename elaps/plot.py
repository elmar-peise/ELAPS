#!/usr/bin/env python
"""Plotting routines for reports."""
from __future__ import division, print_function

from report import Report, apply_stat

from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


default_colors = [
    "#004280", "#e6a500", "#bf0000", "#009999", "#5b59b2", "#969900",
    "#bf0073", "#bf9239", "#004ee6", "#ff7a00"
]

default_styles = {
    "legend": {"color": "#888888"},
    "med": {"linestyle": "-"},
    "min": {"linestyle": "--"},
    "max": {"linestyle": ":", "linewidth": 2},
    "avg": {"linestyle": "-."},
    "min-max": {"hatch": "...", "facecolor": (0, 0, 0, 0)},
    "std": {"alpha": .25},
    "all": {"linestyle": "None", "marker": "."},
}


def plot(datas, stat_names=["med"], colors={}, styles={}, xlabel=None,
         ylabel=None):
    """Plot a series of data sets."""
    styles = default_styles.copy()
    styles.update(styles)

    range_min = min(min(data) for data in datas.values())
    range_max = max(max(data) for data in datas.values())

    if range_min == range_max:
        bar_datas = {
            key: data.values()[0] for key, data in datas
        }
        return bar_plot(bar_datas, stat_names, colors, styles, ylabel)
    else:
        range_datas = {}
        for key, data in datas:
            if min(data) == max(data):
                values = data.values[0]
                range_datas[key] = {range_min: values, range_max: values}
            else:
                range_datas[key] = data
        return range_plot(range_datas, stat_names, colors, styles, xlabel,
                          ylabel)


def range_plot(datas, stat_names=["med"], colors={}, styles={}, xlabel=None,
               ylabel=None):
    """Plot with range on the x axis."""
    fig = Figure()
    axes = fig.gca()

    axes.set_axis_bgcolor("#f0f0f0")
    if hasattr(metric, "name"):
        axes.set_ylabel(metric.name)

    axes.hold(True)

    # plots
    colorpool = defaultcolors[::-1]
    for name, data in datas:
        color = colors.get(name) or colorpool.pop()
        plot_stat_names = stat_names[:]
        if "all" in plot_stat_names:
            # all
            xs = []
            ys = []
            for key, values in data.iteritems():
                for value in values:
                    xs.append(key)
                    ys.append(value)
            axes.plot(xs, ys, color=color, **styles["all"])
            plot_stat_names.remove("all")
        if "min" in plot_stat_names and "max" in plot_stat_names:
            # min-max
            min_data = apply_stat("min", data)
            max_data = apply_stat("max", data)
            xs = sorted(set(min_data) & set(max_data))
            min_ys = [min_data[x] for x in xs]
            max_ys = [max_data[x] for x in xs]
            axes.fill_between(xs, min_ys, max_ys, color=color,
                              **styles["min-max"])
            plot_stat_names.remove("min")
            plot_stat_names.remove("max")
        if "std" in plot_stat_names:
            # std
            std_data = apply_stat("std", data)
            avg_data = apply_stat("avg", data)
            xs = sorted(set(std_data) & set(avg_data))
            min_ys = [avg_data[x] - std_data[x] for x in xs]
            max_ys = [avg_data[x] + std_data[x] for x in xs]
            axes.fill_between(xs, min_ys, max_ys, color=color, **styles["std"])
            plot_stat_names.remove("std")
        for stat_name in plot_stat_names:
            # all other stats
            stat_data = apply_stat(stat_name, data)
            xs = sorted(stat_data)
            ys = [stat_data[x] for x in xs]
            axes.plot(xs, ys, color=color, **styles[stat_name])

    # legend
    colorpool = defaultcolors[::-1]
    legend = []
    for name in datas:
        color = colors.get(name) or colorpool.pop()
        legend.append((Line2D([], [], color=color, **styles["legend"]), name))
    legend_stat_names = stat_names[:]
    if "min" in legend_stat_names and "max" in legend_stat_names:
        legend_stat_names.insert(0, "min-max")
        legend_stat_names.remove("min")
        legend_stat_names.remove("max")
    for stat_name in legend_stat_names:
        if stat_name in ("min-max", "std"):
            legend.append((Patch(**styles["legend"]), stat_name))
        else:
            legend.append((Line2D([], [], **styles["legend"]), stat_name))
    axes.legend(*zip(*legend), loc=0, numpoints=3)

    return fig


def bar_plot(datas, stat_names=["med"], colors={}, styles={}, ylabel=None):
    """Barplot."""
    fig = Figure()
    axes = fig.gca()

    axes.set_axis_bgcolor("#f0f0f0")
    if hasattr(metric, "name"):
        axes.set_ylabel(metric.name)

    axes.hold(True)

    # TODO

    return fig


def plot_report(report, statames=["med"], colors={}, styles={}):
    """Plot a Report."""
    # TODO
