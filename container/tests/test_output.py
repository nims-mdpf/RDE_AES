import os
import shutil
from typing import Union, List


def setup_inputdata_folder(inputdata_name: Union[str, List[str]]):
    """テスト用でdataフォルダ群の作成とrawファイルの準備

    Args:
        inputdata_name (Union[str, List[str]]): rawファイル名
    """

    destination_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    if os.path.exists(destination_path):
        shutil.rmtree(destination_path)

    destination_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(destination_path, exist_ok=True)
    os.makedirs(os.path.join(destination_path, "inputdata"), exist_ok=True)
    os.makedirs(os.path.join(destination_path, "invoice"), exist_ok=True)

    inputdata_original_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "inputdata", "AES-depth"
    )

    if isinstance(inputdata_name, list):
        for item in inputdata_name:
            shutil.copy(
                os.path.join(inputdata_original_path, item),
                os.path.join(destination_path, "inputdata"),
            )
    else:
        shutil.copy(
            os.path.join(inputdata_original_path, inputdata_name),
            os.path.join(destination_path, "inputdata"),
        )

    shutil.copy(
        os.path.join(inputdata_original_path, "invoice.json"),
        os.path.join(destination_path, "invoice"),
    )

    # tasksupport
    tasksupport_original_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "AES-depth", "tasksupport"
    )
    tasksupport_dest_path = os.path.join(destination_path, "tasksupport")
    os.makedirs(tasksupport_dest_path, exist_ok=True)

    for fname in ["default_value.csv", "invoice.schema.json", "metadata-def.json", "rdeconfig.yaml"]:
        shutil.copy(
            os.path.join(tasksupport_original_path, fname),
            os.path.join(tasksupport_dest_path, fname),
        )

class TestOutputCase1:
    """LakeShore形式のマルチファイルテスト:
       - "AES_Depth_profile_Spectral_Set_data_excel_invoice.xlsx",
       - "data092.zip"
    """

    inputdata: Union[str, List[str]] = [
        "AES_Depth_profile_Spectral_Set_data_excel_invoice.xlsx",
        "data092.zip"
    ]

    def test_setup(self):
        setup_inputdata_folder(self.inputdata)

    def test_nonshared_raw(self, setup_main, data_path):
        # ルートのnonshared_rawに必要なフォルダ・ファイルがあるか
        base = os.path.join(data_path, "nonshared_raw")
        assert os.path.isfile(os.path.join(base, "data"))
        assert os.path.isfile(os.path.join(base, "id"))
        assert os.path.isfile(os.path.join(base, "para"))
        assert os.path.isfile(os.path.join(base, "retrotospec.history"))

        # divided配下
        base_div = os.path.join(data_path, "divided", "0001", "nonshared_raw")
        assert os.path.isfile(os.path.join(base_div, "data"))
        assert os.path.isfile(os.path.join(base_div, "id"))
        assert os.path.isfile(os.path.join(base_div, "para"))
        assert os.path.isfile(os.path.join(base_div, "retrotospec.history"))

    def test_main_image(self, data_path):
        assert os.path.exists(os.path.join(data_path, "main_image", "id.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "main_image", "id.png"))

    def test_other_image(self, data_path):
        base = os.path.join(data_path, "other_image")
        base_div = os.path.join(data_path, "divided", "0001", "other_image")

        for fname in ["id_C.png", "id_Hf.png", "id_HfNVV.png", "id_O.png", "id_Si.png"]:
            assert os.path.exists(os.path.join(base, fname))
            assert os.path.exists(os.path.join(base_div, fname))

    def test_structured(self, data_path):
        assert os.path.exists(os.path.join(data_path, "structured", "id.csv"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "structured", "id.csv"))

    def test_thumbnail(self, data_path):
        assert os.path.exists(os.path.join(data_path, "thumbnail", "id.png"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "thumbnail", "id.png"))

    def test_meta(self, data_path):
        assert os.path.exists(os.path.join(data_path, "meta", "metadata.json"))
        assert os.path.exists(os.path.join(data_path, "divided", "0001", "meta", "metadata.json"))
