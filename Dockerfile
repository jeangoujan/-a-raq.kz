FROM python:3.12 AS requirements-stage

WORKDIR /tmp

RUN curl -sSL https://install.python-poetry.org | python3 - --version 2.0.1 && \
    export PATH="/root/.local/bin:$PATH"

RUN /root/.local/bin/poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock /tmp/

RUN ls -la /tmp

RUN /root/.local/bin/poetry export --without-hashes -f requirements.txt --output requirements.txt

FROM python:3.12

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY . .

CMD ["sh", "./scripts/launch.sh"]
