FROM python:3.6.7-slim

ENV PYTHONUNBUFFERED 1
RUN apt-get update --fix-missing --no-install-recommends && \
    apt-get upgrade -y && \
    apt-get install -y build-essential \
    python-dev git \
    libffi-dev libssl-dev libpq-dev \
    wget && \
    pip install -U --no-cache-dir pip setuptools wheel ipython && \
    wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -P /usr/bin/ && chmod +x /usr/bin/wait-for-it.sh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*



COPY api/requirements.txt /src/api/requirements.txt
COPY data_handlers/requirements.txt /src/data_handlers/requirements.txt
COPY tests/requirements.txt /src/tests/requirements.txt

RUN pip install --no-cache-dir -r /src/api/requirements.txt \
                --no-cache-dir -r /src/data_handlers/requirements.txt \
                --no-cache-dir -r /src/tests/requirements.txt

COPY api /src/api
COPY data_handlers /src/data_handlers
COPY tests /src/tests/

RUN pip install -e /src/data_handlers \
                -e /src/api \
                -e /src/tests

COPY .flake8 /src
COPY docker/test_entrypoint.sh /entrypoint.sh
WORKDIR /src

ENTRYPOINT ["bash", "/entrypoint.sh"]
