#
# Virtual environment creation image
#
FROM python:3.12.3-slim AS venv

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/venv/bin:$PATH" \
    POETRY_VIRTUALENVS_IN_PROJECT=true
RUN set -xe \
    # python
    && pip install --upgrade poetry \
    # clean up
    && true

WORKDIR /app
COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root
#
# Production image
#
FROM python:3.12.3-slim AS production
ENV PATH="/venv/bin:$PATH" \
    LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
# Updating image and installing tzdata package, enabling container timezone customization by TZ environment variable
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
# Defining default non-root container user
ARG USER_UID=10000
ARG USER_GID=10001
RUN addgroup --gid $USER_GID app && \
    adduser --uid $USER_UID --gid $USER_GID --disabled-password --gecos "" --shell /usr/sbin/nologin app
# Installing "gosu" for easy step-down from root
# https://github.com/tianon/gosu/blob/master/INSTALL.md
RUN set -eux; \
    apt-get update; \
    apt-get install -y gosu netcat-traditional curl; \
    rm -rf /var/lib/apt/lists/*; \
    # verify that the binary works
    gosu nobody true
WORKDIR /app

# Copying application venv
COPY --from=venv --chown=app:app /app/.venv /app/.venv

# Safe configuration environment
USER root
RUN mkdir -p /var/lib/bistudio
RUN chown -R app:app /var/lib/bistudio

# Copying application files
COPY --chown=app:app ./ ./
RUN mkdir /app/bags.vectordb 
RUN chown -R app:app /app/bags.vectordb

RUN chmod +x ./docker-entrypoint.sh
RUN chmod +x ./stack
RUN chmod +x ./wait-for-it.sh


ENTRYPOINT [ "./docker-entrypoint.sh" ]

EXPOSE 8000