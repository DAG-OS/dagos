FROM ubuntu:hirsute

RUN apt update -y \
    && apt install -y --no-install-recommends \
        curl \
        grep \
        jq \
        podman \
        python3 \
        python3-pip \
        sudo

RUN curl -sSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh --output /tmp/miniconda-installer.sh \
    && sh /tmp/miniconda-installer.sh -b -p $HOME/miniconda \
    && ln -s $HOME/miniconda/bin/conda /usr/local/bin \
    && rm /tmp/miniconda-installer.sh

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 - \
    && ln -s /root/.poetry/bin/poetry /usr/local/bin

WORKDIR /root/dagos
COPY pyproject.toml poetry.lock ./
RUN poetry install

ENTRYPOINT [ "poetry", "run", "tox", "-e", "integration" ]

# TODO: Add sudo user for some tests
#RUN useradd --create-home dev --groups sudo \
#   && echo 'dev:dev' | chpasswd
#USER dev
#WORKDIR /home/dev
