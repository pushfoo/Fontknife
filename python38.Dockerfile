# Temporary local testing setup for Python 3.8
#
# It's easiest to run this with the included Make script.
# See doc/DOCKER.md for more info.

FROM python:3.8

WORKDIR /app

# Core project files required to run the program / tests
COPY ./fontknife/ ./fontknife/
COPY ./tests/ ./tests/
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
CMD bash container.sh