FROM dagos-test-environment

ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /root/dagos
COPY pyproject.toml poetry.lock ./
RUN poetry install

ENTRYPOINT [ "poetry", "run", "tox", "-e", "integration" ]

# TODO: Add sudo user for some tests
#RUN useradd --create-home dev --groups sudo \
#   && echo 'dev:dev' | chpasswd
#USER dev
#WORKDIR /home/dev
