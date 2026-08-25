# AES用テンプレート

## 概要
AES(オージェ電子分光装置)データの登録をする方に適したテンプレートです。以下の測定データ種に対応しています。
- DT0018
    - AES-survey
- DT0019
    - AES-depth


AESの専門家によって監修されたメタ情報を上記ファイルから自動的にRDEが抽出します。
- AESスペクトル（survey）と深さ方向測定スペクトル（depth）に対応したメタ情報の抽出、データを可読化し、オージェ電子検出強度の可視化。
- エクセルインボイス対応

## メタ情報
- [メタ情報](docs/要件定義_AES.xlsx)

## 基本情報

## 使い方
複数データの一括投入に対応している。

一括投入する場合は、
- 送り状情報を記載したエクセルインボイス
- 1つのzipファイルにまとめたデータファイル

の2ファイルを投入する。

なお、zipファイル内のデータは以下のように配置すること。
```
data.zip
 |
 |- [データ名1] (※ zipで固めない)
 |    |- data
 |    |- id
 |    |- para
 |
 |- [データ名2]
 |    | ... 
```

### 入力ファイル
- ./data/inputdata/data
- ./data/inputdata/id
- ./data/inputdata/para

### 出力ファイル
- ./data/raw/
- ./data/structured/\*.csv
- ./data/main_image/\*.png
- ./data/other_image/\*_\*.png

## 構成

### レポジトリ構成

```
aes
├── README.md
├── container
│   ├── Dockerfile
│   ├── data(入出力(下記参照))
│   ├── main.py
│   ├── modules (ソースコード)
│   │   ├── __init__.py
│   │   └── datasets_process.py
│   ├── modules_aes
│   │   ├── __init__.py
│   │   ├── graph_handler.py
│   │   ├── inputfile_handler.py
│   │   ├── interfaces.py
│   │   ├── meta_handler.py
│   │   └── structured_handler.py
│   ├── pip.conf
│   ├── pyproject.toml
│   ├── requirements-test.txt
│   ├── requirements.txt
│   ├── tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_meta.py
│   │   └── test_output.py
│   └── tox.ini
├── docs (ドキュメント)
│   ├── manual (マニュアル)
│   └── 要件定義_AES.xlsx (要件定義)
├── inputdata (サンプルデータ)
│   ├── AES-depth (depth向け)
│   │   ├── AES_Depth_profile_Spectral_Set_data_excel_invoice.xlsx
│   │   ├── data092.zip
│   │   └── invoice.json
│   └── AES-survey (survey向け)
│       ├── AES_Reference_Spectral_Set_57_excel_invoice.xlsx
│       ├── data.zip
│       └── invoice.json
├── templates
│   ├── AES-depth (depth向け)
│   │   ├── batch.yaml
│   │   ├── catalog.schema.json (カタログ項目定義)
│   │   ├── invoice.schema.json (送り状項目定義)
│   │   ├── jobs.template.yaml
│   │   ├── metadata-def.json (メタデータ定義)
│   │   └── tasksupport
│   │       ├── default_value.csv
│   │       ├── invoice.schema.json (送り状項目定義)
│   │       ├── metadata-def.json (メタデータ定義)
│   │       └── rdeconfig.yaml (設定ファイル)
│   └── AES-survey (survey向け)
│       ├── batch.yaml
│       ├── catalog.schema.json (カタログ項目定義)
│       ├── invoice.schema.json (送り状項目定義)
│       ├── jobs.template.yaml
│       ├── metadata-def.json (メタデータ定義)
│       └── tasksupport
│           ├── default_value.csv
│           ├── invoice.schema.json (送り状項目定義)
│           ├── metadata-def.json (メタデータ定義)
│           └── rdeconfig.yaml (設定ファイル)
└── tryout
    ├── invoice_sample.json
    └── tryout.md
```
### 動作環境ファイル入出力
```
│   ├── container/data
│   │   ├── inputdata
│   │   │   └── 登録ファイル欄にドラッグアンドドロップした任意のファイル
│   │   ├── invoice  (送り状ファイル)
│   │   │   └── invoice.json
│   │   ├── logs ( ログファイル)
│   │   │   └── rdesys.log
│   │   ├── main_image
│   │   │   └── (メイン)プロット画像
│   │   ├── meta
│   │   │   └── metadata.json (主要パラメータメタ情報ファイル)
│   │   ├── nonshared_raw
│   │   │   └── inputdataからコピーした入力ファイル
│   │   ├── other_image
│   │   │   └── (メイン以外の)プロット画像
│   │   ├── raw
│   │   ├── structured
│   │   │   └── id.csv (プロット画像元データ)
│   │   ├── tasksupport (テンプレート群)
│   │   │   ├── default_value.csv
│   │   │   ├── invoice.schema.json
│   │   │   ├── metadata-def.json
│   │   │   └── rdeconfig.yaml
│   │   └── thumbnail
│   │       └── *.png (サムネイル用)プロット画像
```
## データ閲覧
- データ一覧画面を開く。
- ギャラリー表示タブでは１データがタイル状に並べられている。データ名をクリックして詳細を閲覧する。
- ツリー表示タブではタクソノミーにしたがってデータを階層表示する。データ名をクリックして詳細を閲覧する。

### 動作環境
- Python: 3.12
- RDEToolKit: 1.7.1
