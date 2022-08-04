FROM python:3.10-slim AS base

RUN apt-get update && apt-get -y upgrade

ENV VIRTUAL_ENV=/opt/env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONBUFFERED=1

RUN python -m venv $VIRTUAL_ENV
RUN pip install --upgrade pip setuptools wheel

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install -r requirements.txt


FROM base AS dev

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

ENV PYTHONPATH=/opt/app/src
COPY . .
RUN pip install -e .

FROM base AS prod-build

COPY . .
RUN pip install .

FROM python:3.10-slim AS prod-api

ENV VIRTUAL_ENV=/opt/env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=prod-build /opt/env /opt/env

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--capture-output", "mailer.wsgi"]

FROM prod-api AS prod-cleaner

CMD ["python", "-m", "sharethis.jobs.cleaner"]
