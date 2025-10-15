from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter

from modules_aes.interfaces import IGraphPlotter


class GraphPlotter(IGraphPlotter[pd.DataFrame]):
    """Template class for creating graphs and visualizations.

    This class serves as a template for the development team to create graphs and visualizations.
    It implements the IGraphPlotter interface. Developers can use this template class as a
    foundation for adding specific graphing logic and customizations based on the project's
    requirements.

    Args:
        df (pd.DataFrame): The DataFrame containing data to be plotted.
        save_path (Path): The path where the generated graph will be saved.

    Keyword Args:
        header (Optional[list[str]], optional): A list of column names to use as headers in the graph.
            Defaults to None.

    Example:
        graph_plotter = GraphPlotter()
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        graph_plotter.plot(data, 'graph.png', header=['X Axis', 'Y Axis'])

    """

    def __init__(self, config: dict[str, str | None] | None = None):
        if config is None:
            config = {}
        self.config = config

    def _init_figure(self) -> tuple[Figure, Axes]:
        """Initialize a matplotlib figure and axes with predefined settings.

        Returns:
            tuple[Figure, Axes]: Created figure and axes objects with customized formatting.

        """
        fig, ax = plt.subplots(figsize=(6.4, 4.8))
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
        ax.grid(ls=":")
        fig.subplots_adjust(left=0.17, bottom=0.155, right=0.95, top=0.9)
        return fig, ax

    def _read_option(self, csv_path: Path) -> dict[str, Any]:
        """Parse CSV file header options prefixed with '#' into a dictionary.

        Args:
            csv_path (Path): Path to the CSV file to read.
            enc (str, optional): Encoding of the CSV file. Defaults to "utf_8".

        Returns:
            dict: Parsed options from CSV header lines.

        """
        axis_unit_index = 2
        axis_inverse_index = 3
        opt: dict[str, Any] = {}
        axis = []

        with csv_path.open("r", encoding="utf-8") as f:
            for row in csv.reader(f):
                if not row or not row[0].startswith("#"):
                    continue

                tokens = [row[0][1:].strip()] + [tok.strip() for tok in row[1:]]
                if tokens[0] == "title":
                    opt[tokens[0]] = tokens[1]
                elif tokens[0] == "dimension":
                    axis = tokens[1:]
                    opt[tokens[0]] = axis
                elif tokens[0] in axis:
                    opt[f"axisName_{tokens[0]}"] = tokens[1]
                    if len(tokens) > axis_unit_index:
                        opt[f"axisUnit_{tokens[0]}"] = tokens[2]
                    if len(tokens) > axis_inverse_index:
                        opt[f"axisInverse_{tokens[0]}"] = True
                elif tokens[0] == "legend":
                    opt["legend"] = tokens[1:]
                else:
                    opt[tokens[0]] = tokens[1:]

        return opt

    def _plot_series(self, df: pd.DataFrame, opt: dict[str, Any], title: str, output_path: Path, show_legend: bool = True) -> None:
        """Plot data series from a DataFrame according to options and save to an image file.

        Args:
            df (pd.DataFrame): DataFrame containing the data to plot.
            opt (dict): Dictionary of plot options (axis labels, scales, inversion flags, etc).
            title (str): Title for the plot.
            output_path (Path): Path to save the output image.
            show_legend (bool, optional): Whether to show the legend. Defaults to True.

        """
        fig, ax = self._init_figure()

        # 軸反転
        if opt.get("axisInverse_x", False):
            ax.invert_xaxis()
        if opt.get("axisInverse_y", False):
            ax.invert_yaxis()

        # スケール
        if opt.get("axisScale_x") == "log":
            ax.set_xscale("log")
        if opt.get("axisScale_y") == "log":
            ax.set_yscale("log")

        # 軸ラベル
        xlabel = opt.get("axisName_x", df.columns[0])
        ylabel = opt.get("axisName_y", df.columns[1])
        if "axisUnit_x" in opt:
            xlabel += f" ({opt['axisUnit_x']})"
        if "axisUnit_y" in opt:
            ylabel += f" ({opt['axisUnit_y']})"
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)

        # プロット
        x_factor = float(opt.get("scaleFactor_x", 1.0))
        y_factor = float(opt.get("scaleFactor_y", 1.0))
        for i in range(0, len(df.columns), 2):
            ax.plot(
                x_factor * df.iloc[:, i], y_factor * df.iloc[:, i + 1], lw=1, label=df.columns[i + 1],
            )

        if show_legend:
            ax.legend()

        fig.tight_layout()
        fig.savefig(output_path)
        plt.close(fig)

    def plot_corrected_original(self, csv_path: Path, out_dir_main_img: Path, out_dir_other_img: Path) -> None:
        """Read data from a CSV file and generate the main image as well as images for each series.

        Args:
            csv_path (Path): Path to the CSV file.
            out_dir_main_img (Path): Output directory for the main image.
            out_dir_other_img (Path): Output directory for other images.

        """
        basename = csv_path.stem
        opt = self._read_option(csv_path)
        df = pd.read_csv(csv_path, comment="#", header=None)

        if "legend" not in opt or "dimension" not in opt:
            err_msg = "CSV header must include both #legend and #dimension."
            raise ValueError(err_msg)

        # カラム名の割り当て
        legends = opt["legend"]
        dims = opt["dimension"]
        num_series = len(legends)
        expected_cols = num_series * len(dims)
        if df.shape[1] != expected_cols:
            err_msg = (
                f"CSV column count does not match expected value: "
                f"{df.shape[1]} columns found, expected {expected_cols} (legend × dimension)."
            )
            raise ValueError(err_msg)

        column_names = []
        for legend in legends:
            for i in range(len(dims) - 1):
                column_names.append(f"{legend}_{i}")
            column_names.append(legend)

        df.columns = pd.Index(column_names)

        # メイン画像（すべての系列を重ねて描画）
        main_output = out_dir_main_img / f"{basename}.png"
        self._plot_series(df, opt, opt.get("title", basename), main_output, show_legend=(num_series > 1))

        # 系列ごとの画像
        for i in range(0, df.shape[1], 2):
            df_sub = df.iloc[:, i:i + 2]
            label = df.columns[i + 1]
            if label == "Survey":
                continue
            title = f"{opt.get('title', basename)}_{label}"
            other_output = out_dir_other_img / f"{basename}_{label}.png"
            self._plot_series(df_sub, opt, title, other_output, show_legend=False)
