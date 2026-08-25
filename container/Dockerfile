## Python Version:3.12
FROM python:3.12-slim-trixie

ARG PIP_TRUSTED_HOST

# appディレクトリを作成
WORKDIR /app

# プログラムや設定ファイルなどをコピーする
COPY main.py /app
COPY requirements.txt /app
COPY modules/ /app/modules/ 
COPY modules_aes/ /app/modules_aes/

# 必要なPythonライブラリのインストール
RUN pip install --upgrade pip && pip install -r requirements.txt