FROM opensuse/leap:15.6 as base

ARG UID
ENV UID=${UID:-9999}
ARG GID
ENV GID=${GID:-9999}

# We might be running as a user which already exists in this image. In that situation
# Everything is OK and we should just continue on.
RUN groupadd -g $GID ufo_docker_group || exit 0
RUN useradd --shell /bin/bash -u $UID -g $GID -o -c "" -m ufo_docker_user -l || exit 0
ENV DOCKER_USER=ufo_docker_user

RUN zypper addrepo --repo https://download.opensuse.org/repositories/devel:languages:python:Factory/15.6/devel:languages:python:Factory.repo --name pythonfactory
RUN zypper --gpg-auto-import-keys install -y \
    python311 python311-pip

USER $UID:$GID

RUN python3.11 -m pip install --user pipx
RUN python3.11 -m pipx ensurepath

ENV PATH="$PATH:/home/ufo_docker_user/.local/bin"

RUN pipx install pdm

ENV PDM_CHECK_UPDATE=false

COPY --chown=$UID:$GID README.md pyproject.toml pdm.lock /tmp/

WORKDIR /

ENV PDM_CACHE_DIR=/tmp/ufo_pdm_cache
RUN --mount=type=cache,mode=777,target=$PDM_CACHE_DIR,uid=$UID,gid=$GID pdm install --check --prod --no-editable --project /tmp/

ENV PATH="/tmp/.venv/bin:$PATH"

WORKDIR /project

COPY --chown=$UID:$GID src /project/

# Ensure that Python outputs everything that's printed inside
# the application rather than buffering it.
ENV PYTHONUNBUFFERED 1

ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-"settings"}
CMD ["sh", "-c", "pgwait && gunicorn wsgi --log-file - --bind 0.0.0.0:8000"]
