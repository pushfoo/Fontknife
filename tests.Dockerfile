# Helper for running arbitary Python versions
#
# It's easiest to run this with the included script (test_python38.sh)
# See doc/DOCKER.md for more info.
ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION} AS base

WORKDIR /app

# Core project files required to run the program / tests
COPY ./fontknife/ ./fontknife/
COPY ./tests/ ./testse/
COPY ./pyproject.toml ./

# A helper test script
COPY ./container.sh .
RUN chmod +x container.sh

# Since the environment is disposable, the easiest option with Docker
# is to skip a virtual environment.
RUN python -m pip install --upgrade pip wheel setuptools
RUN python -m pip install -e .[dev]

# Set the container to run the helper script unless
# otherwise specified by docker run -i -t $YOUR_COMMAND_HERE
CMD [ 'bash', 'container.sh' ]