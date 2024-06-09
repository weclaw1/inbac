FROM python:3.8-slim-bookworm AS build
ENV POETRY_VERSION=1.8.3 \
    VIRTUAL_ENV=/venv \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y \
    curl \
    binutils \
    python3-tk

ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV
RUN curl -sSL https://install.python-poetry.org | python -

WORKDIR /app

COPY . .

RUN poetry install && poetry run pyinstaller --onefile --windowed --hidden-import='PIL._tkinter_finder' inbac/inbac.py


FROM debian:12-slim
RUN apt-get update && apt-get install -y\
    libxcb1 fonts-recommended

ARG USERNAME=inbac
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

COPY --from=build --chown=$USER_UID:$USER_GID /app/dist/inbac /inbac

USER $USERNAME
CMD ["/inbac"]
