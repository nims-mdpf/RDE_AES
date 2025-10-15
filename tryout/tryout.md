# RDEデータセットテンプレート　RDE_AES　を試してみる

RDEデータセットテンプレート `RDE_AES`　をローカル開発環境で動かす方法を説明します。

なお、入力する測定データ(RAWデータ)は提供していませんので各自でご用意ください。

## 準備
以下の開発環境を用意してください。
- python ver3.11以上
  - RDEの構造化処理プログラムはpythonを用いています 
- pyenvなど仮想環境で動作させることを推奨
  - この説明ではpyenvを利用

ファイル一式の入手
- git cloneまたはdownload zipでファイル一式を取得
- zipファイルで取得した場合は適宜フォルダに解凍する
- この説明では入手したファイルの解凍先を `work` フォルダと呼ぶことにします

## ファイルなどの説明
workフォルダには以下の内容のフォルダが用意されています
- container
  - 構造化処理プログラム一式が含まれています
  - このフォルダの下でテスト実行します
  - 利用するpythonのパッケージはrequirements.txtを参照
- docs
  - 説明書など 
- template
  - 構造化処理プログラム以外のデータセットテンプレートを構成するファイルが含まれています
  - テンプレートによって含まれるファイルの構成が異なります

## 動かしてみる、それと解説

動かしてみるまでの手順は以下の通り
1. 仮想環境作成
2. ファイルの配置
3. プログラムの実行

テンプレートの選択
- RDE_AESデータセットテンプレートはAESスペクトル（survey）と深さ方向測定スペクトル（depth）のファイルに対応しています。
- 利用時はsurvey、depthのいずれかを選択します(送状定義に差異があるため両型式を同時に扱うことはできません)
- templateフォルダには、survey用、depth用それぞれのテンプレートが収められています


### 仮想環境作成
ターミナルを使ったコマンドラインでの操作で説明します(Ubuntu24.04上)
1. workフォルダに移動
2. containerに移動
    ```cmd
    $ cd container
    ```
3. containerの内容　展開した状態では以下の通り
    ```cmd
    $ ls
    Dockerfile  main.py  modules  modules_aes  pip.conf  pyproject.toml  requirements-test.txt  requirements.txt  tox.ini
    ```
4. 仮想環境作成(pyenvの事例)
    ```cmd
    $ pyenv local 3.11.13
    $ python -m venv venv
    $ . venv/bin/activate
    (venv) $ pip install pip --upgrade
    ```
5. pythonパッケージの導入(pipとrequirements.txtを利用して)
   - この作業でrdetoolkitなどが導入されます
    ```cmd
    (venv) $ pip install -r requirements.txt
    ```
6. 構造化処理プログラムの入出力用のフォルダを作成
    ```cmd
    (venv) $ mkdir data
    ```
7. 入力ファイル用フォルダを作成
    ```cmd
    (venv) $ mkdir data/inputdata
    ```
8. 送状用フォルダを作成
    ```cmd
    (venv) $ mkdir data/invoice
    ```
9.  構造化処理用補助ファイル用のフォルダを作成
    ```cmd
    (venv) $ mkdir data/tasksupport
    (venv) $ tree data
    data
    ├── inputdata
    ├── invoice
    └── tasksupport    
    ```
10. テンプレートファイルの配置
  - tasksupportフォルダに以下のようにファイルをコピーします
  - ここではAES-depth用テンプレートを選択しています
    ```cmd
    (venv) $ cp -p  ../templates/AES-depth/tasksupport/* data/tasksupport/
    (venv) $ tree data
    data
    ├── inputdata
    ├── invoice
    └── tasksupport
        ├── default_value.csv
        ├── invoice.schema.json
        ├── metadata-def.json
        └── rdeconfig.yaml
    ```
11. 入力データの配置
    - 入力データをdata/inputdata以下に配置します
    - 入力データは各自ご用意してください
    - この説明ではAES_Depth_data_excel_invoice.xlsx, data092.zip というファイルを使っています
```cmd
(venv) $ $ cp ../inputdata/AES-depth/AES_Depth_profile_Spectral_Set_data_excel_invoice.xlsx data/inputdata
(venv) $ $ cp ../inputdata/AES-depth/data092.zip data/inputdata
```
12. 送状ファイルの配置
    - 送状ファイル(invoice.json)をdata/invoice以下に配置します
    - テスト用のサンプルを利用してください
    ```cmd
    (venv) $ cp  ../tryout/invoice_sample.json data/invoice/invoice.json
    ```
13. ファイル配置の確認
    - 以下のようにファイルが配置されていれば準備完了です
    ```cmd
    (venv) $ tree data
    data
    ├── inputdata
    │   ├── AES_Depth_data_excel_invoice.xlsx
    │   └── data092.zip
    ├── invoice
    │   └── invoice.json
    └── tasksupport
        ├── default_value.csv
        ├── invoice.schema.json
        ├── metadata-def.json
        └── rdeconfig.yaml
    ```
14. それでは動かしてみましょう
    - エラーメッセージなど返ってこなければ成功です
    ```cmd
    $ python main.py
    ```
15. 確認
    - 正常終了すると以下のようにファイルが出力されます
    ```cmd
    (venv) $ tree data
    data
    ├── attachment
    ├── inputdata
    │   ├── AES_Depth_data_excel_invoice.xlsx
    │   └── data092.zip
    ├── invoice
    │   └── invoice.json
    ├── invoice_patch
    ├── logs
    │   └── rdesys.log
    ├── main_image
    │   └── id.png
    ├── meta
    │   └── metadata.json
    ├── nonshared_raw
    │   ├── data
    │   ├── id
    │   └── para
    ├── other_image
    │   ├── id_C.png
    │   ├── id_Hf.png
    │   ├── id_HfNVV.png
    │   ├── id_O.png
    │   └── id_Si.png
    ├── raw
    ├── structured
    │   └── id.csv
    ├── tasksupport
    │   ├── default_value.csv
    │   ├── invoice.schema.json
    │   ├── metadata-def.json
    │   └── rdeconfig.yaml
    ├── temp
    │   ├── data092
    │   │   └── HfO2-data092-001.A
    │   │       ├── data
    │   │       ├── id
    │   │       └── para
    │   │   
    │   └── invoice_org.json
    └── thumbnail
        └── id.png
    ```