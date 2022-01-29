FROM python:3-slim

RUN apt update -y \
    && apt install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --output /tmp/miniconda-installer.sh \
    && sh /tmp/miniconda-installer.sh -b -p $HOME/miniconda \
    && ln -s $HOME/miniconda/bin/conda /usr/local/bin \
    && /usr/local/bin/conda clean --all \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - \
    && ln -s /root/.poetry/bin/poetry /usr/local/bin \
    && rm -rf /root/.poetry/lib/poetry/_vendor/py2.7 \
    && rm -rf /root/.poetry/lib/poetry/_vendor/py3.5 \
    && rm -rf /root/.poetry/lib/poetry/_vendor/py3.6 \
    && rm -rf /tmp/* \
    && rm -rf /var/cache/debconf/*

WORKDIR /root/dagos
COPY pyproject.toml poetry.lock ./
RUN poetry install

ENTRYPOINT [ "poetry", "run", "tox", "-e", "integration" ]

# TODO: Add sudo user for some tests
#RUN useradd --create-home dev --groups sudo \
#   && echo 'dev:dev' | chpasswd
#USER dev
#WORKDIR /home/dev
