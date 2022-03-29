FROM ghcr.io/binkhq/python:3.9

WORKDIR /app
ADD . .

RUN apt update && apt -y install gcc vim nano tmux postgresql-client nginx && \
    pipenv install --deploy --system --ignore-pipfile && \
    mv /app/router/nginx.conf /etc/nginx && \
    apt-get autoremove -y gcc && rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]
