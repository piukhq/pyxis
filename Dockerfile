FROM ghcr.io/binkhq/python:3.9

WORKDIR /app
ADD . .

RUN apt update && apt -y install vim nano tmux postgresql-client && \
    pipenv install --deploy --system --ignore-pipfile && \
    rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]
