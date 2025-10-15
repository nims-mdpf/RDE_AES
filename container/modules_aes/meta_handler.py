from __future__ import annotations

import csv
from datetime import datetime as dt
from pathlib import Path

from natsort import natsorted
from rdetoolkit.models.rde2types import MetaType, RepeatedMetaType
from rdetoolkit.rde2util import Meta

from modules_aes.interfaces import IMetaParser


class MetaParser(IMetaParser[MetaType]):
    """Parses metadata and saves it to a specified path.

    This class is designed to parse metadata from a dictionary and save it to a specified path using
    a provided Meta object. It can handle both constant and repeated metadata.

    Attributes:
        const_meta_info (MetaType | None): Dictionary to store constant metadata.
        repeated_meta_info (RepeatedMetaType | None): Dictionary to store repeated metadata.

    """

    def __init__(self, *, metadata_def_json_path: Path | None = None, meta_default_vals_file_path: Path | None = None):
        self.meta_default_vals_file_path = meta_default_vals_file_path
        self.const_meta_info: MetaType = {}
        self.repeated_meta_info: RepeatedMetaType = {}
        self.metadata_def_json_path = metadata_def_json_path
        if self.metadata_def_json_path is None:
            error_msg = "metadata_def_json_path must be specified"
            raise ValueError(error_msg)
        self.meta_obj = Meta(self.metadata_def_json_path)
        """Init."""

    def parse(self, dct_hdr: dict, data_mode: str | None) -> tuple[MetaType, RepeatedMetaType]:
        """Parse and extract constant and repeated metadata from the provided data."""
        default_vals = self._load_default_vals()
        const_meta = self._extract_const_meta(dct_hdr)
        self._apply_conversions(dct_hdr, const_meta)
        variable_meta = self._extract_variable_meta(dct_hdr, data_mode)
        self.const_meta_info = {**default_vals, **const_meta}
        self.repeated_meta_info = variable_meta
        return self.const_meta_info, self.repeated_meta_info

    def _load_default_vals(self) -> dict:
        default_vals = {}
        try:
            if self.meta_default_vals_file_path is not None:
                with open(self.meta_default_vals_file_path, encoding="utf_8") as f:
                    for row in csv.DictReader(f):
                        default_vals[row["key"]] = row["value"]
        except FileNotFoundError:
            pass
        return default_vals

    def _extract_const_meta(self, dct_hdr: dict) -> MetaType:
        sp_k_raw_list = [
            "AP_ACQDATE", "AP_PCURRENT", "AP_CHAMBER_PRESS", "AP_SPC_ANAMOD",
            "AP_SPC_ES", "AP_DATATYPE", "AP_SPC_ROI_NOFEXE",
        ]
        return {k: v for k, v in dct_hdr.items() if isinstance(v, str) and k not in sp_k_raw_list}

    def _apply_conversions(self, dct_hdr: dict, const_meta: MetaType) -> None:
        self._convert_analyzer_mode(dct_hdr, const_meta)
        self._convert_datatype(dct_hdr, const_meta)
        self._convert_ign_neut_mode(dct_hdr, const_meta)
        self._convert_acqdate(dct_hdr, const_meta)
        self._convert_pcurrent_chamber_press(dct_hdr, const_meta)
        self._convert_sposn_fields(dct_hdr, const_meta)
        self._convert_beam_mode(const_meta)
        self._convert_comment(dct_hdr, const_meta)

    def _convert_analyzer_mode(self, dct_hdr: dict, const_meta: MetaType) -> None:
        val_analyzer_mode = dct_hdr.get("AP_SPC_ANAMOD", "")
        if val_analyzer_mode == "1":
            const_meta["AP_SPC_ES"] = dct_hdr.get("AP_SPC_ES", "")
            const_meta["AP_SPC_ANAMOD"] = "CAE"
        elif val_analyzer_mode in {"2", "3", "4", "5"}:
            const_meta["AP_SPC_ANAMOD"] = "CRR"
        else:
            const_meta["AP_SPC_ANAMOD"] = "unknown"

    def _convert_datatype(self, dct_hdr: dict, const_meta: MetaType) -> None:
        dt_map = {
            "1": "SEM image",
            "3": "Wide",
            "4": "Narrow",
            "5": "Depth",
            "7": "Line",
            "8": "Auger image",
        }
        if "AP_DATATYPE" in dct_hdr:
            const_meta["AP_DATATYPE"] = dt_map.get(dct_hdr["AP_DATATYPE"], "unknown")

    def _convert_ign_neut_mode(self, dct_hdr: dict, const_meta: MetaType) -> None:
        ign_map = {
            "1": "inactive",
            "2": "active",
        }
        if "AP_IGN_NEUT_MODE" in dct_hdr:
            const_meta["AP_IGN_NEUT_MODE"] = ign_map.get(dct_hdr["AP_IGN_NEUT_MODE"], "unknown")

    def _convert_acqdate(self, dct_hdr: dict, const_meta: MetaType) -> None:
        if "AP_ACQDATE" in dct_hdr:
            dt_measured = dt.strptime(dct_hdr["AP_ACQDATE"], "%Y%m%d%H%M%S")
            const_meta["measurement.measured_date"] = dt_measured.isoformat()
            const_meta["operation_date_time_year"] = dt_measured.year
            const_meta["operation_date_time_month"] = dt_measured.month
            const_meta["operation_date_time_day"] = dt_measured.day
            const_meta["operation_date_time_hour"] = dt_measured.hour
            const_meta["operation_date_time_minute"] = dt_measured.minute
            const_meta["operation_date_time_second"] = dt_measured.second

    def _convert_pcurrent_chamber_press(self, dct_hdr: dict, const_meta: MetaType) -> None:
        parts_expected_length = 2
        for k in ["AP_PCURRENT", "AP_CHAMBER_PRESS"]:
            if k in dct_hdr:
                parts = dct_hdr[k].split()
                if len(parts) == parts_expected_length:
                    const_meta[k] = f"{parts[0]}x10^(-{parts[1]})"

    def _convert_sposn_fields(self, dct_hdr: dict, const_meta: MetaType) -> None:
        for k in [
            "AP_SPOSN_PDIA", "AP_SPOSN_BEAM_P1X", "AP_SPOSN_BEAM_P1Y",
            "AP_SPOSN_BEAM_P2X", "AP_SPOSN_BEAM_P2Y", "AP_SPOSN_BSMOD",
        ]:
            if k in dct_hdr and isinstance(dct_hdr[k], dict):
                last_key = natsorted(dct_hdr[k].keys())[-1]
                const_meta[k] = dct_hdr[k][last_key]

    def _convert_beam_mode(self, const_meta: MetaType) -> None:
        beam_mode_map = {
            "1": "Spot",
            "2": "Scan",
            "3": "Limited Scan",
        }
        if const_meta.get("AP_SPOSN_BSMOD"):
            const_meta["AP_SPOSN_BSMOD"] = beam_mode_map.get(str(const_meta["AP_SPOSN_BSMOD"]), "unknown")

    def _convert_comment(self, dct_hdr: dict, const_meta: MetaType) -> None:
        if "AP_COMMENT" in dct_hdr:
            const_meta["AP_COMMENT"] = dct_hdr["AP_COMMENT"][-1] if isinstance(dct_hdr["AP_COMMENT"], list) else dct_hdr["AP_COMMENT"]

    def _extract_variable_meta(self, dct_hdr: dict, data_mode: str | None) -> dict:
        variable_meta: dict = {}
        if data_mode == "AES-narrow":
            key_pairs = [
                ("AP_SPC_ROI_START", "abscissa_start"),
                ("AP_SPC_ROI_STOP", "abscissa_end"),
                ("AP_SPC_ROI_STEP", "abscissa_increment"),
                ("AP_SPC_ROI_DWELL", "collection_time"),
                ("AP_SPC_ROI_NAME", "species_label_transitions"),
                ("AP_SPC_ROI_SWEEPS", "total_acquisition_number"),
            ]
            for k_raw, k_meta in key_pairs:
                if k_raw in dct_hdr and isinstance(dct_hdr[k_raw], dict):
                    variable_meta[k_meta] = [dct_hdr[k_raw][kk] for kk in natsorted(dct_hdr[k_raw].keys())]
        elif data_mode == "AES-survey":
            key_pairs = [
                ("AP_SPC_WSTART", "abscissa_start"),
                ("AP_SPC_WSTOP", "abscissa_end"),
                ("AP_SPC_WSTEP", "abscissa_increment"),
                ("AP_SPC_WDWELL", "collection_time"),
                ("AP_SPC_WSWEEPS", "total_acquisition_number"),
            ]
            for k_raw, k_meta in key_pairs:
                if k_raw in dct_hdr:
                    variable_meta[k_meta] = [dct_hdr[k_raw]]
        return variable_meta

    def save_meta(
        self,
        save_path: Path,
        meta_obj: Meta | None = None,
        *,
        const_meta_info: MetaType | None = None,
        repeated_meta_info: RepeatedMetaType | None = None,
    ) -> None:
        """Save parsed metadata to a file using the provided Meta object.

        Args:
            save_path (Path): The path where the metadata will be saved.
            meta_obj (Meta): The Meta object that handles operate of metadata.
            const_meta_info (MetaType | None): The constant metadata to save. Defaults to the
            internal const_meta_info if not provided.
            repeated_meta_info (RepeatedMetaType | None): The repeated metadata to save. Defaults
            to the internal repeated_meta_info if not provided.

        Returns:
            str: The result of the meta assignment operation.

        """
        if meta_obj is None:
            meta_obj = self.meta_obj
        if const_meta_info is None:
            const_meta_info = self.const_meta_info
        if repeated_meta_info is None:
            repeated_meta_info = self.repeated_meta_info

        meta_obj.assign_vals(const_meta_info)
        meta_obj.assign_vals(repeated_meta_info)

        meta_obj.writefile(str(save_path))
