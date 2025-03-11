FROM python:3.12.7-slim as builder

RUN mkdir /scheduler_full
COPY /src/. /scheduler_full
WORKDIR /scheduler_full

RUN apt-get update \
    && pip install --upgrade pip \
    && pip install --user -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*


ENV PATH=/root/.local:$PATH

CMD ["python", "./__main__.py"]