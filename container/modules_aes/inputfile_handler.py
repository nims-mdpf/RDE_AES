from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from natsort import natsorted
from rdetoolkit.rde2util import CharDecEncoding

from modules_aes.interfaces import IInputFileParser


class FileReader(IInputFileParser):
    """Template class for reading and parsing input data.

    This class serves as a template for the development team to read and parse input data.
    It implements the IInputFileParser interface. Developers can use this template class
    as a foundation for adding specific file reading and parsing logic based on the project's
    requirements.

    Args:
        raw_file_paths (tuple[Path, ...]): Paths to input source files.

    Returns:
        Any: The loaded data from the input file(s).

    Example:
        file_reader = FileReader()
        loaded_data = file_reader.read(('file1.txt', 'file2.txt'))
        file_reader.to_csv('output.csv')

    """

    def _tokenize_line(self, ln: str) -> list[str]:
        tokens = []
        ln_left = ln.strip()
        while ln_left != "":
            pos_key = ln_left.find("$AP_")
            if pos_key == -1:
                tokens.append(ln_left.strip())
                break
            if pos_key > 0:
                tokens.append(ln_left[:pos_key].strip())
            tokens_tmp = ln_left[pos_key:].split(maxsplit=1)
            tokens.append(tokens_tmp[0])
            ln_left = tokens_tmp[1] if len(tokens_tmp) > 1 else ""
        return tokens

    def data_process(
        self,
        tokens: list[str],
        k: str,
        dct_hdr: dict[str, Any],
        raw_file_path_para: Path,
    ) -> str:
        """Process a list of tokens, update the metadata dictionary, and return the current key.

        Args:
            tokens (list[str]): Tokenized elements from a line of the input file.
            k (str): The current key being processed.
            dct_hdr (dict): Dictionary used to store the parsed metadata.
            raw_file_path_para (Path): Path to the input parameter file.

        Returns:
            str: The updated current key.

        """
        key_names_list_val = [
            "AP_SPC_HISTORY",
            "AP_COMMENT",
        ]

        key_names_dict_val = [
            "AP_SPC_CEMSTAT",
            "AP_SPC_ROI_EXEMOD",
            "AP_SPC_ROI_NAME",
            "AP_SPC_ROI_START",
            "AP_SPC_ROI_STOP",
            "AP_SPC_ROI_STEP",
            "AP_SPC_ROI_POINTS",
            "AP_SPC_ROI_DWELL",
            "AP_SPC_ROI_SWEEPS",
            "AP_SPC_ROI_ACQRSF",
            "AP_SPOSN_EXEMOD",
            "AP_SPOSN_NAME",
            "AP_SPOSN_BSMOD",
            "AP_SPOSN_PDIA",
            "AP_SPOSN_BEAMX",
            "AP_SPOSN_BEAMY",
            "AP_SPOSN_RESOLN",
            "AP_SPOSN_BEAM_P1X",
            "AP_SPOSN_BEAM_P1Y",
            "AP_SPOSN_BEAM_P2X",
            "AP_SPOSN_BEAM_P2Y",
            "AP_SPOSN_PIXELS_X",
            "AP_SPOSN_PIXELS_Y",
            "AP_SPC_ROI_DISPMOD",
            "AP_SPC_ROI_XSHIFT",
            "AP_SPC_ROI_XSTART",
            "AP_SPC_ROI_XSTOP",
            "AP_SPC_ROI_YSHIFT",
            "AP_SPC_ROI_YSTART",
            "AP_SPC_ROI_YSTOP",
            "AP_SPC_ROI_YGAIN",
            "AP_SPC_ROI_RSF",
        ]

        for tok in tokens:
            if tok.startswith("$AP_"):
                k0 = tok[4:]  # "$AP_"を除外した部分を記憶
                k = "" if k0 == "END_" + k else k0
            elif k != "":
                kk = "AP_" + k
                if kk in key_names_list_val:
                    if kk not in dct_hdr:
                        dct_hdr[kk] = []
                    cast(list[Any], dct_hdr[kk]).append(tok)
                elif kk in key_names_dict_val:
                    if kk not in dct_hdr:
                        dct_hdr[kk] = {}
                    vv = tok.split(maxsplit=1)
                    cast(dict[str, str], dct_hdr[kk])[vv[0]] = vv[1]
                else:
                    if kk in dct_hdr:
                        error_msg = f"unknown duplicated key found in {raw_file_path_para}"
                        raise ValueError(error_msg)
                    dct_hdr[kk] = tok
            else:
                error_msg = f"failed to parse {raw_file_path_para}"
                raise ValueError(error_msg)

        return k

    def read_para_file(self, raw_file_path_para: Path) -> tuple[dict[str, Any], str | None]:
        """Parse a parameter file into metadata and determine the data mode.

        This method reads a parameter file, extracting keys and values with special handling for list-type
        and dictionary-type entries. Keys starting with "$AP_" are processed, with specific keys treated
        as lists or dictionaries based on predefined categories. The method also identifies the data mode
        ("AES-survey" or "AES-narrow") based on the value of "AP_DATATYPE".

        Args:
            raw_file_path_para (Path): Path to the parameter text file to be parsed.

        Returns:
            tuple: A tuple containing:
                - dict: Parsed metadata with keys and values of various types.
                - str or None: Data mode ("AES-survey" or "AES-narrow"), or None if undefined.

        Raises:
            ValueError: If the file format is invalid, contains duplicated unknown keys,
                        or the data mode is undefined.

        """
        dct_hdr: dict[str, Any] = {}

        enc = CharDecEncoding.detect_text_file_encoding(raw_file_path_para)
        k = ""

        with open(raw_file_path_para, encoding=enc) as f:
            for ln in f:
                if ln.startswith("#"):
                    continue
                tokens = self._tokenize_line(ln)
                k = self.data_process(tokens, k, dct_hdr, raw_file_path_para)

        if "AP_DATATYPE" not in dct_hdr:
            error_msg = f'data mode undefined in file "{raw_file_path_para}"'
            raise ValueError(error_msg)

        data_mode = {
            "3": "AES-survey",
            "4": "AES-narrow",
        }.get(dct_hdr["AP_DATATYPE"], None)

        return dct_hdr, data_mode

    def read_data_spe_file(self, raw_file_path_data: Path, data_mode: str, dct_hdr: dict[str, str | int | float | list[Any] | bool | dict[str, str]]) -> list[list[int]]:
        """Read binary data from the specified file and organize it into lists based on the data mode.

        This method reads a binary file 4 bytes at a time (big-endian) and converts each chunk into an integer.
        Depending on the `data_mode`, it structures the data differently:
        - For "AES-survey", all data is returned as a single list.
        - For "AES-narrow", the data is split into multiple lists based on ROI (Region of Interest) points
          specified in the header dictionary `dct_hdr`.

        Args:
            raw_file_path_data (Path): Path to the binary data file to be read.
            data_mode (str): Mode specifying how the data should be interpreted ("AES-survey" or "AES-narrow").
            dct_hdr (MetaType): Header metadata dictionary containing information such as ROI names and points.

        Returns:
            list[list[int]]: A list of integer lists representing the parsed data segments.

        Raises:
            ValueError: If `data_mode` is not recognized.

        """
        # バイナリファイルから4バイトずつ読み出し、paramで指定された個数ごとのデータを格納した配列で返す関数
        output_list = []
        with open(raw_file_path_data, "rb") as fid:
            # ビッグエンディアンでの4バイト数値データとして読み込んでいく
            while bbb := fid.read(4):
                output_list.append(int.from_bytes(bbb, "big"))

        data_obj = []
        if data_mode == "AES-survey":
            data_obj.append(output_list)
        elif data_mode == "AES-narrow":
            # 可読ファイル生成時に各物質のデータの区切れ位置を処理すると1関数で行う処理が非常に多くなるため
            shift_point = 0
            roi_name_dict = cast(dict[str, str], dct_hdr["AP_SPC_ROI_NAME"])
            for key_roi in natsorted(roi_name_dict.keys()):
                n_points_curr = int(cast(dict[str, str], dct_hdr["AP_SPC_ROI_POINTS"])[key_roi])
                data_obj.append(output_list[shift_point: shift_point + n_points_curr])
                shift_point += n_points_curr
        else:
            error_msg = f'unknown data mode "{data_mode}"'
            raise ValueError(error_msg)

        return data_obj
