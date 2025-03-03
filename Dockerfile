FROM python:3.12 AS requirements-stage
WORKDIR /tmp
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir poetry poetry-core
COPY ./pyproject.toml ./poetry.lock /tmp/
RUN poetry export --with dev -f requirements.txt --output requirements.txt --without-hashes



FROM python:3.12
WORKDIR /code
COPY --from=requirements-stage /tmp/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
