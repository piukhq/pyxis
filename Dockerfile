FROM ghcr.io/binkhq/python:3.10-poetry

WORKDIR /app
ADD . .

RUN poetry config virtualenvs.create false
RUN apt update && apt -y install gcc vim nano tmux postgresql-client nginx && \
    poetry install && \
    mv /app/router/nginx.conf /etc/nginx && \
    apt-get autoremove -y gcc && rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]
