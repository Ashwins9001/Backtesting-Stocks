FROM apache/airflow:3.1.8-python3.11

# 1️⃣ Switch to root to install OS dependencies
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        gcc \
        g++ \
        libpq-dev \
        libssl-dev \
        libffi-dev \
        python3-dev \
        libbz2-dev \
        liblzma-dev \
        zlib1g-dev \
        curl \
        wget \
        git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2️⃣ Switch back to airflow user for pip installs
USER airflow

# 3️⃣ Upgrade pip, setuptools, wheel
RUN python -m pip install --upgrade pip setuptools wheel

# 4️⃣ Install Python packages as airflow user
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    yfinance \
    pyarrow \
    psycopg2-binary \
    matplotlib