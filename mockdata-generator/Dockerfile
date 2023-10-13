# syntax=docker/dockerfile:1.3
ARG WORKDIR=/app \
# python 只能設定到 major.minor，不能設定到 patch
# 否則 /usr/loca/lib 會找不到套件
    PYTHON_VERSION=3.11 \
    ALPINE_VERSION=3.17 \
    PYTHON_PACKAGE=/usr/local/lib/python${PYTHON_VERSION}/site-packages

#############################################
# 編譯 Python 套件
#############################################
FROM python:${PYTHON_VERSION}-slim as builder-base
ARG WORKDIR
# Don't buffer `stdout`:
ENV PYTHONUNBUFFERED=1
# 控制在編譯 Python 時會不會生成 .pyc 檔案
# 1 代表不生成，0 代表生成
ENV PYTHONDONTWRITEBYTECODE 1

# 下載 poetry
# 參考 https://github.com/python-poetry/poetry/issues/1178
RUN --mount=type=cache,target=/root/.cache/pip,id=py_pkg,sharing=locked \
    set -xe && \
    pip install --upgrade pip && \
    pip install poetry && \
    pip install setuptools && \
# 讓 poetry 生成的虛擬環境在專案裡
    poetry config virtualenvs.in-project true

WORKDIR ${WORKDIR}

# 複製基本的設定檔
COPY --chmod=755 pyproject.toml config.py ./

RUN --mount=type=cache,target=/root/.cache/pypoetry,id=my_poetry,sharing=locked \
    set -xe && poetry install


#############################################
#! 沒用到
# 安裝 Oracle Client
#
# 不支援 arm64
#############################################
FROM alpine:${ALPINE_VERSION} as oracle_builder
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add libaio libnsl

# 安裝 oracle client
# 如果本地的 /tmp 有檔案，cache會抓本地的，沒有才下載
RUN --mount=type=cache,target=/tmp,id=oracle_exe,sharing=locked \
    set -xe && \
    rm -rf /tmp/instantclient_21_8 && \
    wget -O /tmp/oracle_client.zip https://download.oracle.com/otn_software/linux/instantclient/218000/instantclient-basic-linux.x64-21.8.0.0.0dbru.zip && \
# 解壓縮
    unzip /tmp/oracle_client.zip -d /tmp && \
    mkdir -p /opt/oracle/lib && \
    mv /tmp/instantclient_21_8/ /opt/oracle/instantclient && \
# 複製特定檔案
    cp /usr/lib/libaio.so.1 /opt/oracle/instantclient/ && \
    cp /lib/libc.musl-x86_64.so.1 /opt/oracle/instantclient/ && \
# 做軟連接讓 libclntsh.so 能被 Python 找到
    ln -s /opt/oracle/instantclient/libclntsh.so.21.1 /opt/oracle/lib/libclntsh.so && \
    rm /tmp/oracle_client.zip


#############################################
# 把環境變數寫入 settings.yml
#############################################
FROM alpine:${ALPINE_VERSION} AS envsubst
# 因為 ARG 在構建階段等同於 ENV，所以 envsubst 可以寫入檔案裡。
# 這裡是要加載替換字符
ARG ORACLE_IP
ARG ORACLE_PORT
ARG ORACLE_DATABASE
ARG ORACLE_USER
ARG ORACLE_PASSWORD

RUN --mount=type=cache,target=/var/cache/apk,id=apk \
    --mount=type=bind,source=settings.template,target=settings.template \
    set -xe && \
    # 安裝 gettext，讓 envsubst 可以使用
    apk add gettext && \
    # 替換環境變數
    envsubst '${ORACLE_IP}${ORACLE_PORT}${ORACLE_USER}${ORACLE_PASSWORD}${ORACLE_DATABASE}' < settings.template > settings.toml


#############################################
# 開發環境建置
#############################################
FROM python:${PYTHON_VERSION} as dev
ARG WORKDIR
ARG PYTHON_VERSION
ARG PYTHON_PACKAGE

# 設定 PYTHON PATH，讓 venv 可以讀取本地模組
# 沒寫的話會出現 ModuleNotFoundError: No module named 'lib'
ENV PYTHONPATH=${WORKDIR} \
# 設定 Python 解譯器的路徑
    PATH=${WORKDIR}/.venv/bin:${PATH}
# 這一行是讓 Python 能找到 Oracle Client 的 *.so
    # LD_LIBRARY_PATH=/opt/oracle/instantclient

WORKDIR ${WORKDIR}

# 安裝 OpenJDK 17，讓 VS Code 的 Database Client 模組可以使用 Oracle
# RUN --mount=type=cache,target=/var/cache/apt \
#     --mount=type=cache,target=/var/lib/apt \
#     set -xe && apt-get update && apt-get install -y openjdk-17-jdk

# 複製 poetry
# 一定要複製 site-packages，不然會出現 ModuleNotFoundError: No module named 'poetry'
COPY --from=builder-base --chmod=777 /usr/local/bin/poetry* /usr/local/bin/
COPY --from=builder-base --chmod=777 /usr/local/bin/setuptools* /usr/local/bin/
COPY --from=builder-base --chmod=777 ${PYTHON_PACKAGE}/ ${PYTHON_PACKAGE}/
# 複製虛擬環境
COPY --from=builder-base --chmod=777 ${WORKDIR} .
# 複製 oracle 的檔案
# COPY --from=oracle_builder /opt/oracle /opt/oracle
# 因為設定檔最常修改，所以放最後複製
COPY --from=envsubst settings.toml .

CMD ["tail", "-f", "/dev/null"]