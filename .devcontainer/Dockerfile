FROM python:3.8-slim-bookworm
ENV POETRY_VERSION=1.8.3 \
    VIRTUAL_ENV=/venv \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y \
    curl \
    binutils \
    git \
    nano \
    python3-tk

ARG USERNAME=inbac
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN mkdir -p $POETRY_HOME
RUN chown $USER_UID:$USER_GID $POETRY_HOME

RUN mkdir -p $VIRTUAL_ENV
RUN chown $USER_UID:$USER_GID $VIRTUAL_ENV

USER $USERNAME

ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV
RUN curl -sSL https://install.python-poetry.org | python -