from __future__ import annotations

import csv
from datetime import datetime as dt
from itertools import zip_longest
from pathlib import Path
from typing import Any, cast

from natsort import natsorted

from modules_aes.interfaces import IStructuredDataProcesser


class StructuredDataProcesser(IStructuredDataProcesser):
    """Template class for parsing structured data.

    This class serves as a template for the development team to read and parse structured data.
    It implements the IStructuredDataProcesser interface. Developers can use this template class
    as a foundation for adding specific file reading and parsing logic based on the project's
    requirements.

    Example:
        csv_handler = StructuredDataProcesser()
        df = pd.DataFrame([[1,2,3],[4,5,6]])
        loaded_data = csv_handler.to_csv(df, 'file2.txt')

    """

    def write_fnd_csv_file_survey(self, csv_file_path: Path, dct_hdr: dict[str, str | int | float | list[Any] | bool | dict[str, str]], data_obj: list[list[int]]) -> None:
        """Write AES survey mode data extracted from the raw data file to a CSV file.

        This function generates a CSV file containing metadata headers and spectral data suitable for
        plotting AES survey spectra. Metadata such as acquisition date, acquisition time, and comments
        are included in the CSV header. The data section includes kinetic energy values and corresponding
        intensity counts.

        Args:
            csv_file_path (Path): Path to the output CSV file.
            dct_hdr (MetaType): Metadata dictionary extracted from the parameter file.
            data_obj (list[list[int]]): List containing one list of intensity data points for the survey mode.

        Returns:
            None

        """
        # dataファイルから抽出したデータをcsvファイルへ出力する関数

        str_title = ""
        if "AP_COMMENT" in dct_hdr:
            comment = dct_hdr["AP_COMMENT"]
            if isinstance(comment, list) and len(comment) > 0:
                str_title = str(comment[0])

        with open(csv_file_path, "w", newline="", encoding="utf-8") as write_fid:
            # csvファイル出力用の変数を設定
            writer = csv.writer(write_fid, delimiter=",", lineterminator="\n")

            writer.writerow(["#title", str_title])
            writer.writerow(["#dimension", 'x', 'y'])
            writer.writerow(['#x', 'Kinetic Energy', 'eV'])
            writer.writerow(['#y', 'Intensity', 'counts'])
            # 元素名はJEOLのパラメータファイルからははっきりとわかるものがないためSurveyとする
            writer.writerow(['#legend', 'Survey'])
            dt_obj = dt.strptime(str(dct_hdr["AP_ACQDATE"]), "%Y%m%d%H%M%S")
            writer.writerow(['#acq_date', dt_obj.strftime("%Y/%m/%d %H:%M:%S")])
            # 生データの値をそのままグラフ化する方針に決定したためcps変換を実行されないようにする
            writer.writerow(['#cps_conversion', 0])
            writer.writerow(['#acq_time', dct_hdr['AP_SPC_WDWELL']])  # 引用元が"survey"と"narrow"で異なるので注意
            writer.writerow(['#acq_time_unit', 'ms'])
            writer.writerow(['#subplot', 0, 1, 1])
            # csvファイルに項目を記載
            mode_write_data = ['##comment']
            if dct_hdr['AP_DATATYPE'] in ("3", "4"):
                mode_write_data.append('AES(JEOL)spectrum')
            elif dct_hdr['AP_DATATYPE'] == "5":
                mode_write_data.append('AES(JEOL)depth')
            else:
                mode_write_data.append('')
            writer.writerow(mode_write_data)

            # データ部分と項目記載の前には改行を1つ加える取り決めのため
            writer.writerow('')

            # data_objにはリストオブジェクトが一つのみ保持されている単一系列データと想定する
            kinetic_energy_values = []
            tmp_start = float(str(dct_hdr["AP_SPC_WSTART"]))
            tmp_step = float(str(dct_hdr["AP_SPC_WSTEP"]))
            kinetic_energy_values.append([tmp_start + tmp_step * i for i in range(len(data_obj[0]))])
            kinetic_energy_values.append(list(data_obj[0]))
            for line_data_list in zip_longest(*kinetic_energy_values, fillvalue=""):
                writer.writerow(line_data_list)

    def write_fnd_csv_file_narrow(self, csv_file_path: Path, dct_hdr: dict[str, str | int | float | list[Any] | bool | dict[str, str]], data_obj: list[list[int]]) -> None:
        """Write extracted data from a data file to a specified CSV file in a narrow format.

        Args:
            csv_file_path (Path): The path to the output CSV file.
            dct_hdr (MetaType): A dictionary containing header metadata such as AP_COMMENT, AP_SPC_ROI_NAME, etc.
            data_obj (list[list[int]]): A list of intensity data arrays, each corresponding to a region of interest (ROI).

        Description:
            - Extracts meta information such as title, acquisition date, ROI names, and acquisition times from the header dictionary,
              and writes these to the CSV file header.
            - Writes a comment line describing the AES data type based on the data type.
            - Calculates the x-axis values (Kinetic Energy) for each ROI using the start value, step size, and number of points,
              and writes these values alongside the corresponding intensity data.
            - Inserts a blank line before the data section as a formatting convention.
            - Does not perform cps conversion; raw data values are output as-is.

        Note:
            The output CSV is structured for further plotting or analysis, keeping raw spectral data intact.

        """
        # dataファイルから抽出したデータをcsvファイルへ出力する関数

        def _get_val_list(_dct_hdr: Any, _key: Any) -> list[str | int | float | bool]:
            dct = _dct_hdr[_key]
            return [dct[k] for k in natsorted(dct.keys())]

        str_title = ""
        if "AP_COMMENT" in dct_hdr:
            comment = dct_hdr["AP_COMMENT"]
            if isinstance(comment, list) and len(comment) > 0:
                str_title = str(comment[0])

        with open(csv_file_path, "w", newline="", encoding="utf-8") as write_fid:
            # csvファイル出力用の変数を設定
            writer = csv.writer(write_fid, delimiter=",", lineterminator="\n")

            writer.writerow(["#title", str_title])
            writer.writerow(["#dimension", 'x', 'y'])
            writer.writerow(['#x', 'Kinetic Energy', 'eV'])
            writer.writerow(['#y', 'Intensity', 'counts'])
            writer.writerow(['#legend'] + _get_val_list(dct_hdr, "AP_SPC_ROI_NAME"))
            dt_obj = dt.strptime(str(dct_hdr["AP_ACQDATE"]), "%Y%m%d%H%M%S")
            writer.writerow(['#acq_date', dt_obj.strftime("%Y/%m/%d %H:%M:%S")])
            # 生データの値をそのままグラフ化する方針に決定したためcps変換を実行されないようにする
            writer.writerow(['#cps_conversion', 0])
            writer.writerow(['#acq_time'] + _get_val_list(dct_hdr, "AP_SPC_ROI_DWELL"))
            writer.writerow(['#acq_time_unit', 'ms'])
            writer.writerow(['#subplot', 0, 1, 1])
            # csvファイルに項目を記載
            mode_write_data = ['##comment']
            if dct_hdr['AP_DATATYPE'] in ("3", "4"):
                mode_write_data.append('AES(JEOL)spectrum')
            elif dct_hdr['AP_DATATYPE'] == "5":
                mode_write_data.append('AES(JEOL)depth')
            else:
                mode_write_data.append('')
            writer.writerow(mode_write_data)

            # データ部分と項目記載の前には改行を1つ加える取り決めのため
            writer.writerow('')

            # x軸の値はstartの値からステップ幅と点数をかけたものになるため
            kinetic_energy_values = []
            roi_start_dict = cast(dict[str, str], dct_hdr['AP_SPC_ROI_START'])
            roi_step_dict = cast(dict[str, str], dct_hdr['AP_SPC_ROI_STEP'])
            roi_points_dict = cast(dict[str, str], dct_hdr['AP_SPC_ROI_POINTS'])
            if 'AP_SPC_ROI_NAME' in dct_hdr and isinstance(dct_hdr['AP_SPC_ROI_NAME'], dict):
                for idx_roi, key_roi in enumerate(natsorted(dct_hdr['AP_SPC_ROI_NAME'].keys())):
                    tmp_start = float(roi_start_dict[key_roi])
                    tmp_step = float(roi_step_dict[key_roi])
                    n_pnts = int(roi_points_dict[key_roi])
                    kinetic_energy_values.append([tmp_start + tmp_step * i for i in range(n_pnts)])
                    kinetic_energy_values.append(list(data_obj[idx_roi]))

            for line_data_list in zip_longest(*kinetic_energy_values, fillvalue=""):
                writer.writerow(line_data_list)
