FROM python:3.10-slim

# 必要なパッケージをインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    vim \
    zsh \
    sudo \
    ca-certificates \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Pythonのパッケージ管理ツールを最新にアップグレード
RUN pip install --upgrade pip

# 不足しているPythonライブラリをインストール
RUN pip install --no-cache-dir \
    numpy \
    scipy \
    pandas \
    matplotlib \
    seaborn \
    jupyterlab \
    scikit-learn \
    plotly

WORKDIR /mnt