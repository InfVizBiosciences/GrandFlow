# wdecoster
"""
This module provides functions for plotting data extracted from Oxford Nanopore sequencing
reads and alignments, but some of it's functions can also be used for other applications.


FUNCTIONS
* Check if a specified color is a valid matplotlib color
check_valid_color(color)
* Check if a specified output format is valid
checkvalidFormat(format)
* Create a bivariate plot with dots, hexbins and/or kernel density estimates.
Also arguments for specifying axis names, color and xlim/ylim
scatter(x, y, names, path, color, format, plots, stat=None, log=False, minvalx=0, minvaly=0)
* Create cumulative yield plot and evaluate read length and quality over time
timePlots(df, path, color, format)
* Create length distribution histogram and density curve
lengthPlots(array, name, path, n50, color, format, log=False)
* Create flowcell physical layout in numpy array
makeLayout()
* Present the activity (number of reads) per channel on the flowcell as a heatmap
spatialHeatmap(array, title, path, color, format)

"""
import base64
import io
import logging
import sys
import urllib
from collections import namedtuple
from datetime import timedelta
from math import ceil

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import colors as mcolors


# from pauvre.marginplot import margin_plot
# import plotly
# import plotly.graph_objs as go


class Plot(object):
    """A Plot object is defined by a path to the output file and the title of the plot."""

    def __init__(self, path, title):
        self.path = path
        self.title = title
        self.fig = None
        self.html = None

    def encode(self):
        if self.html:
            return self.html
        elif self.fig:
            return self.encode2()
        else:
            return self.encode1()

    def encode1(self):
        """Return the base64 encoding of the figure file and insert in html image tag."""
        data_uri = base64.b64encode(open(self.path,
                                         'rb').read()).decode('utf-8').replace(
                                             '\n', '')
        return '<img src="data:image/png;base64,{0}">'.format(data_uri)

    def encode2(self):
        """Return the base64 encoding of the fig attribute and insert in html image tag."""
        buf = io.BytesIO()
        self.fig.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        return '<img src="data:image/png;base64,{0}">'.format(
            urllib.parse.quote(string))


class Layout(object):
    def __init__(self, structure, template, xticks, yticks):
        self.structure = structure
        self.template = template
        self.xticks = xticks
        self.yticks = yticks


def check_valid_color(color):
    """Check if the color provided by the user is valid.

    If color is invalid the default is returned.
    """
    if color in list(mcolors.CSS4_COLORS.keys()) + ["#4CB391"]:
        logging.info("grandplot: Valid color {}.".format(color))
        return color
    else:
        logging.info(
            "grandplot: Invalid color {}, using default.".format(color))
        sys.stderr.write("Invalid color {}, using default.\n".format(color))
        return "#4CB391"


def check_valid_format(figformat):
    """Check if the specified figure format is valid.

    If format is invalid the default is returned.
    Probably installation-dependent
    """
    fig = plt.figure()
    if figformat in list(fig.canvas.get_supported_filetypes().keys()):
        logging.info("grandplot: valid output format {}".format(figformat))
        return figformat
    else:
        logging.info("grandplot: invalid output format {}".format(figformat))
        sys.stderr.write(
            "Invalid format {}, using default.\n".format(figformat))
        return "png"


def scatter(x,
            y,
            names,
            path,
            plots,
            color="#4CB391",
            figformat="png",
            stat=None,
            log=False,
            minvalx=0,
            minvaly=0,
            title=None,
            **kargs):
    """Create bivariate plots.

    Create four types of bivariate plots of x vs y, containing marginal summaries
    -A scatter plot with histograms on axes
    """
    logging.info(
        "Creating {} vs {} plots using statistics from {} reads.".format(
            names[0], names[1], x.size))
    sns.set(style="ticks")
    maxvalx = np.amax(x)
    maxvaly = np.amax(y)

    plots_made = []

    sns.set(style="darkgrid")
    dot_plot = Plot(
        path=path + "_dot." + figformat,
        title="{} vs {} plot using dots".format(names[0], names[1]))
    sns.set(font_scale=1.5)
    plot = sns.jointplot(
        x=x,
        y=y,
        kind="scatter",
        color=color,
        stat_func=stat,
        xlim=(minvalx, maxvalx),
        ylim=(minvaly, maxvaly),
        space=0,
        size=10,
        joint_kws={"s": 1},
        **kargs)
    plot.set_axis_labels(names[0], names[1], fontsize=20)
    if log:
        dot_plot.title = dot_plot.title + " after log transformation of read lengths"
        ticks = [10**i for i in range(10) if not 10**i > 10 * (10**maxvalx)]
        plot.ax_joint.set_xticks(np.log10(ticks))
        plot.ax_marg_x.set_xticks(np.log10(ticks))
        plot.ax_joint.set_xticklabels(ticks)
    plt.subplots_adjust(top=0.93)
    plot.fig.suptitle(
        "{} vs {}".format(names[0], names[1]) + ' (%s)' % title
        if title else '',
        fontsize=25)
    dot_plot.fig = plot
    plot.savefig(dot_plot.path, format=figformat, dpi=300, bbox_inches="tight")
    plots_made.append(dot_plot)

    plt.close("all")
    return plots_made


def check_valid_time_and_sort(df, timescol, days=5, warning=True):
    """Check if the data contains reads created within the same `days` timeframe.

    if not, print warning and only return part of the data which is within `days` days
    Resetting the index twice to get also an "index" column for plotting the cum_yield_reads plot
    """
    timediff = (df[timescol].max() - df[timescol].min()).days
    if timediff < days:
        return df.sort_values(timescol).reset_index(drop=True).reset_index()
    else:
        if warning:
            sys.stderr.write(
                "\nWarning: data generated is from more than {} days.\n".
                format(str(days)))
            sys.stderr.write(
                "Likely this indicates you are combining multiple runs.\n")
            sys.stderr.write(
                "Plots based on time are invalid and therefore truncated to first {} days.\n\n"
                .format(str(days)))
            logging.warning(
                "Time plots truncated to first {} days: invalid timespan: {} days"
                .format(str(days), str(timediff)))
        return df[df[timescol] < timedelta(days=days)] \
            .sort_values(timescol) \
            .reset_index(drop=True) \
            .reset_index()


def time_plots(df, path, title=None, color="#4CB391", figformat="png"):
    """Making plots of time vs read length, time vs quality and cumulative yield."""
    dfs = check_valid_time_and_sort(df, "start_time")
    logging.info("grandplot: Creating timeplots using {} reads.".format(
        len(dfs)))
    cumyields = cumulative_yield(
        dfs=dfs.set_index("start_time"),
        path=path,
        figformat=figformat,
        title=title,
        color=color)
    violins = violin_plots_over_time(
        dfs=dfs, path=path, figformat=figformat, title=title)
    return cumyields + violins


def violin_plots_over_time(dfs, path, figformat, title):
    maxtime = dfs["start_time"].max().total_seconds()
    time_length = Plot(
        path=path + "TimeLengthViolinPlot." + figformat,
        title="Violin plot of read lengths over time")
    sns.set_style("white")
    labels = [
        str(i) + "-" + str(i + 6) for i in range(0, 168, 6)
        if not i > (maxtime / 3600)
    ]
    dfs['timebin'] = pd.cut(
        x=dfs["start_time"], bins=ceil((maxtime / 3600) / 6), labels=labels)
    ax = sns.violinplot(
        x="timebin", y="lengths", data=dfs, inner=None, cut=0, linewidth=0)
    ax.set(
        xlabel='Interval (hours)',
        ylabel="Read length",
        title=title or time_length.title)
    plt.xticks(rotation=30, ha='center')
    fig = ax.get_figure()
    time_length.fig = fig
    fig.savefig(
        fname=time_length.path, format=figformat, dpi=100, bbox_inches='tight')
    plt.close("all")

    plots = [time_length]

    if "quals" in dfs:
        time_qual = Plot(
            path=path + "TimeQualityViolinPlot." + figformat,
            title="Violin plot of quality over time")
        sns.set_style("white")
        ax = sns.violinplot(
            x="timebin", y="quals", data=dfs, inner=None, cut=0, linewidth=0)
        ax.set(
            xlabel='Interval (hours)',
            ylabel="Basecall quality",
            title=title or time_qual.title)
        plt.xticks(rotation=30, ha='center')
        fig = ax.get_figure()
        time_qual.fig = fig
        fig.savefig(
            fname=time_qual.path,
            format=figformat,
            dpi=100,
            bbox_inches='tight')
        plots.append(time_qual)
        plt.close("all")
    return plots


def cumulative_yield(dfs, path, figformat, title, color):
    cum_yield_gb = Plot(
        path=path + "CumulativeYieldPlot_Gigabases." + figformat,
        title="Cumulative yield")
    s = dfs.loc[:, "lengths"].cumsum().resample('10T').max() / 1e9
    ax = sns.regplot(
        x=s.index.total_seconds() / 3600,
        y=s,
        x_ci=None,
        fit_reg=False,
        color=color,
        scatter_kws={"s": 3})
    ax.set(
        xlabel='Run time (hours)',
        ylabel='Cumulative yield in gigabase',
        title=title or cum_yield_gb.title)
    fig = ax.get_figure()
    cum_yield_gb.fig = fig
    fig.savefig(
        cum_yield_gb.path, format=figformat, dpi=100, bbox_inches="tight")
    plt.close("all")

    cum_yield_reads = Plot(
        path=path + "CumulativeYieldPlot_NumberOfReads." + figformat,
        title="Cumulative yield")
    s = dfs.loc[:, "lengths"].resample('10T').count().cumsum()
    ax = sns.regplot(
        x=s.index.total_seconds() / 3600,
        y=s,
        x_ci=None,
        fit_reg=False,
        color=color,
        scatter_kws={"s": 3})
    ax.set(
        xlabel='Run time (hours)',
        ylabel='Cumulative yield in number of reads',
        title=title or cum_yield_reads.title)
    fig = ax.get_figure()
    cum_yield_reads.fig = fig
    fig.savefig(
        cum_yield_reads.path, format=figformat, dpi=100, bbox_inches="tight")
    plt.close("all")

    num_reads = Plot(
        path=path + "NumberOfReads_Over_Time." + figformat,
        title="Number of reads over time")
    s = dfs.loc[:, "lengths"].resample('10T').count()
    ax = sns.regplot(
        x=s.index.total_seconds() / 3600,
        y=s,
        x_ci=None,
        fit_reg=False,
        color=color,
        scatter_kws={"s": 3})
    ax.set(
        xlabel='Run time (hours)',
        ylabel='Number of reads per 10 minutes',
        title=title or num_reads.title)
    fig = ax.get_figure()
    num_reads.fig = fig
    fig.savefig(num_reads.path, format=figformat, dpi=100, bbox_inches="tight")
    plt.close("all")

    return [cum_yield_gb, cum_yield_reads, num_reads]


def length_plots(array,
                 name,
                 path,
                 title=None,
                 n50=None,
                 color="#4CB391",
                 figformat="png",
                 binsize=100):
    """Create histogram of read lengths."""
    logging.info("grandplot: Creating length plots for {}.".format(name))
    maxvalx = np.amax(array)
    if n50:
        logging.info(
            "grandplot: Using {} reads with read length N50 of {}bp and maximum of {}bp."
            .format(array.size, n50, maxvalx))
    else:
        logging.info("grandplot: Using {} reads maximum of {}bp.".format(
            array.size, maxvalx))

    HistType = namedtuple('HistType', 'weight name binsize ylabel')
    plots = []
    sns.set(style="darkgrid")
    sns.set(font_scale=1.5)
    for h_type in [HistType(None, "", binsize, "Number of reads")]:
        histogram = Plot(
            path=path + "Reads_length_histogram." + figformat,
            title=h_type.name + "Histogram of read lengths")
        ax = sns.distplot(
            a=array,
            kde=False,
            hist=True,
            bins=round(int(maxvalx) / h_type.binsize),
            color=color,
            # hist_kws={"weights": h_type.weight}
        )
        if n50:
            plt.axvline(n50)
            plt.annotate(
                ' N50:{:,}bp'.format(n50),
                xy=(n50, np.amax([h.get_height() for h in ax.patches])),
                size=10)
        ax.set_xlabel('Read length', size=20)
        # Set the ylabel of the graph from here
        ax.set_ylabel(h_type.ylabel, size=20)
        ax.set_title(
            histogram.title + ' (%s)' % title if title else '', size=25)

        # ax.fig.suptitle(histogram.title + ' (%s)' % title if title else '', fontsize=25)
        plt.ticklabel_format(
            style='plain', axis='y')  # repress scientific notation
        fig = ax.get_figure()
        histogram.fig = fig
        fig.set_size_inches(10, 10)
        fig.savefig(
            histogram.path, format=figformat, dpi=300, bbox_inches="tight")
        plt.close("all")

    return plots


def yield_by_minimal_length_plot(array,
                                 name,
                                 path,
                                 title=None,
                                 n50=None,
                                 color="#4CB391",
                                 figformat="png"):
    df = pd.DataFrame(data={"lengths": np.sort(array)[::-1]})
    df["cumyield_gb"] = df["lengths"].cumsum() / 10**9
    yield_by_length = Plot(
        path=path + "Yield_By_Length." + figformat, title="Yield by length")
    ax = sns.regplot(
        x='lengths',
        y="cumyield_gb",
        data=df,
        x_ci=None,
        fit_reg=False,
        color=color,
        scatter_kws={"s": 3})
    ax.set(
        xlabel='Read length',
        ylabel='Cumulative yield for minimal length',
        title=title or yield_by_length.title)
    fig = ax.get_figure()
    yield_by_length.fig = fig
    fig.savefig(
        yield_by_length.path, format=figformat, dpi=100, bbox_inches="tight")
    plt.close("all")
    return yield_by_length


def make_layout(maxval):
    """Make the physical layout of the MinION flowcell.
    based on https://bioinformatics.stackexchange.com/a/749/681
    returned as a numpy array
    """
    if maxval > 512:
        return Layout(
            structure=np.concatenate(
                [
                    np.array([
                        list(range(10 * i + 1, i * 10 + 11)) for i in range(25)
                    ]) + j for j in range(0, 3000, 250)
                ],
                axis=1),
            template=np.zeros((25, 120)),
            xticks=range(1, 121),
            yticks=range(1, 26))
    else:
        layoutlist = []
        for i, j in zip([33, 481, 417, 353, 289, 225, 161, 97],
                        [8, 456, 392, 328, 264, 200, 136, 72]):
            for n in range(4):
                layoutlist.append(
                    list(range(i + n * 8, (i + n * 8) + 8, 1)) +
                    list(range(j + n * 8, (j + n * 8) - 8, -1)))
        return Layout(
            structure=np.array(layoutlist).transpose(),
            template=np.zeros((16, 32)),
            xticks=range(1, 33),
            yticks=range(1, 17))


def spatial_heatmap(array, path, title=None, color="Greens", figformat="png"):
    """Taking channel information and creating post run channel activity plots."""
    logging.info(
        "grandplot: Creating heatmap of reads per channel using {} reads."
        .format(array.size))
    activity_map = Plot(
        path=path + "." + figformat,
        title="Number of reads generated per channel")
    layout = make_layout(maxval=np.amax(array))
    valueCounts = pd.value_counts(pd.Series(array))
    for entry in valueCounts.keys():
        layout.template[np.where(
            layout.structure == entry)] = valueCounts[entry]
    plt.figure()
    ax = sns.heatmap(
        data=pd.DataFrame(
            layout.template, index=layout.yticks, columns=layout.xticks),
        xticklabels="auto",
        yticklabels="auto",
        square=True,
        cbar_kws={"orientation": "horizontal"},
        cmap=color,
        linewidths=0.20)
    ax.set_title(title or activity_map.title)
    fig = ax.get_figure()
    activity_map.fig = fig
    fig.savefig(activity_map.path, format=figformat, dpi=100)
    plt.close("all")
    return [activity_map]


def violin_or_box_plot(df,
                       y,
                       figformat,
                       path,
                       y_name,
                       title=None,
                       violin=True,
                       log=False,
                       palette=None):
    """Create a violin or boxplot from the received DataFrame.

    The x-axis should be divided based on the 'dataset' column,
    the y-axis is specified in the arguments
    """
    violin_comp = Plot(
        path=path + "NanoComp_" + y.replace(' ', '_') + '.' + figformat,
        title="Comparing {}".format(y))
    if y == "quals":
        violin_comp.title = "Comparing base call quality scores"
    if violin:
        logging.info("grandplot: Creating violin plot for {}.".format(y))
        ax = sns.violinplot(
            x="dataset",
            y=y,
            data=df,
            inner=None,
            cut=0,
            palette=palette,
            linewidth=0)
    else:
        logging.info("grandplot: Creating box plot for {}.".format(y))
        ax = sns.boxplot(x="dataset", y=y, data=df, palette=palette)
    if log:
        ticks = [
            10**i for i in range(10) if not 10**i > 10 * (10**np.amax(df[y]))
        ]
        ax.set(yticks=np.log10(ticks), yticklabels=ticks)
    ax.set(title=title or violin_comp.title, ylabel=y_name)
    plt.xticks(rotation=30, ha='center')
    fig = ax.get_figure()
    violin_comp.fig = fig
    fig.savefig(
        fname=violin_comp.path, format=figformat, dpi=100, bbox_inches='tight')
    plt.close("all")
    return [violin_comp]


def output_barplot(df, figformat, path, title=None, palette=None):
    """Create barplots based on number of reads and total sum of nucleotides sequenced."""
    logging.info(
        "grandplot: Creating barplots for number of reads and total throughput."
    )
    read_count = Plot(
        path=path + "NanoComp_number_of_reads." + figformat,
        title="Comparing number of reads")
    ax = sns.countplot(x="dataset", data=df, palette=palette)
    ax.set(ylabel='Number of reads', title=title or read_count.title)
    plt.xticks(rotation=30, ha='center')
    fig = ax.get_figure()
    read_count.fig = fig
    fig.savefig(
        fname=read_count.path, format=figformat, dpi=100, bbox_inches='tight')
    plt.close("all")

    throughput_bases = Plot(
        path=path + "NanoComp_total_throughput." + figformat,
        title="Comparing throughput in gigabases sequenced")
    throughput = df.groupby('dataset')['lengths'].sum()
    ax = sns.barplot(
        x=list(throughput.index),
        y=throughput / 1e9,
        palette=palette,
        order=df["dataset"].unique())
    ax.set(
        ylabel='Total gigabase sequenced',
        title=title or throughput_bases.title)
    plt.xticks(rotation=30, ha='center')
    fig = ax.get_figure()
    throughput_bases.fig = fig
    fig.savefig(
        fname=throughput_bases.path,
        format=figformat,
        dpi=100,
        bbox_inches='tight')
    plt.close("all")
    return read_count, throughput_bases


def compare_cumulative_yields(df, path, palette=None, title=None):
    if palette is None:
        palette = plotly.colors.DEFAULT_PLOTLY_COLORS * 5
    dfs = check_valid_time_and_sort(df, "start_time").set_index("start_time")

    logging.info(
        "grandplot: Creating cumulative yield plots using {} reads.".format(
            len(dfs)))
    cum_yield_gb = Plot(
        path=path + "NanoComp_CumulativeYieldPlot_Gigabases.html",
        title="Cumulative yield")
    data = []
    for d, c in zip(df.dataset.unique(), palette):
        s = dfs.loc[dfs.dataset == d, "lengths"].cumsum().resample(
            '10T').max() / 1e9
        data.append(
            go.Scatter(
                x=s.index.total_seconds() / 3600,
                y=s,
                opacity=0.75,
                name=d,
                marker=dict(color=c)))
    cum_yield_gb.html = plotly.offline.plot(
        {
            "data":
            data,
            "layout":
            go.Layout(
                barmode='overlay',
                title=title or cum_yield_gb.title,
                xaxis=dict(title="Time (hours)"),
                yaxis=dict(title="Yield (gigabase)"),
            )
        },
        output_type="div",
        show_link=False)
    with open(cum_yield_gb.path, 'w') as html_out:
        html_out.write(cum_yield_gb.html)
    return [cum_yield_gb]


def overlay_histogram(df, path, palette=None):
    """
    Use plotly to create an overlay of length histograms
    Return html code

    Only has 10 colors, which get recycled up to 5 times.
    """
    if palette is None:
        palette = plotly.colors.DEFAULT_PLOTLY_COLORS * 5
    overlay_hist = Plot(
        path=path + "NanoComp_OverlayHistogram.html",
        title="Histogram of read lengths")
    data = [
        go.Histogram(
            x=df.loc[df.dataset == d, "lengths"],
            opacity=0.4,
            name=d,
            marker=dict(color=c)) for d, c in zip(df.dataset.unique(), palette)
    ]

    overlay_hist.html = plotly.offline.plot(
        {
            "data": data,
            "layout": go.Layout(barmode='overlay', title=overlay_hist.title)
        },
        output_type="div",
        show_link=False)
    with open(overlay_hist.path, 'w') as html_out:
        html_out.write(overlay_hist.html)

    overlay_hist_normalized = Plot(
        path=path + "NanoComp_OverlayHistogram_Normalized.html",
        title="Normalized histogram of read lengths")
    data = [
        go.Histogram(
            x=df.loc[df.dataset == d, "lengths"],
            opacity=0.4,
            name=d,
            histnorm='probability',
            marker=dict(color=c)) for d, c in zip(df.dataset.unique(), palette)
    ]

    overlay_hist_normalized.html = plotly.offline.plot(
        {
            "data":
            data,
            "layout":
            go.Layout(barmode='overlay', title=overlay_hist_normalized.title)
        },
        output_type="div",
        show_link=False)
    with open(overlay_hist_normalized.path, 'w') as html_out:
        html_out.write(overlay_hist_normalized.html)
    return [overlay_hist, overlay_hist_normalized]


def run_tests():
    import pickle
    df = pickle.load(open("nanotest/sequencing_summary.pickle", "rb"))
    scatter(
        x=df["lengths"],
        y=df["quals"],
        names=['Read lengths', 'Average read quality'],
        path="LengthvsQualityScatterPlot",
        plots={
            'dot': 1,
            'kde': 1,
            'hex': 1,
            'pauvre': 1
        })
    time_plots(df=df, path=".", color="#4CB391")
    length_plots(array=df["lengths"], name="lengths", path=".")
    spatial_heatmap(
        array=df["channelIDs"],
        title="Number of reads generated per channel",
        path="ActivityMap_ReadsPerChannel")


checkvalidColor = check_valid_color
checkvalidFormat = check_valid_format
spatialHeatmap = spatial_heatmap
lengthPlots = length_plots
timePlots = time_plots

if __name__ == "__main__":
    run_tests()
