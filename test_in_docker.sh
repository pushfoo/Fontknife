#!/bin/bash

Usage() {
cat <<EOF
Usage: ${0} PYTHON_VERSION

Run the test suite inside a Docker container. Note that on a Linux
system, Docker requires one of the following:

* Running the post-install instructions to enable rootless Docker usage
* Using the sudo command before any Docker commands

PYTHON_VERSION

  This is any version listed in pyproject.toml

Who's this for?

  Anyone in one or more of these categories:

  * Likes reproducibility and containers
  * Lacks direct access to a supported Python version
  * Wants to run tests in Docker

EOF
}

error() {
  cat <<< "ERROR: $*" 1>&2
}


if [[  "$1" == '--help' ]]; then
  Usage
  exit 0
elif [[ "$1" =~ ^3\.(8|9|10|11|12) ]]; then
  PYTHON_VERSION="$1"
else
  error "Expected a PYTHON_VERSION or --help"
  exit 1
fi


# Command for building the image
docker build\
 -f tests.Dockerfile\
 --build-arg="PYTHON_VERSION=${PYTHON_VERSION}"\
 -t "fontknife:${PYTHON_VERSION}"\
 .


BUILD_RESULT=$?


if [ $BUILD_RESULT -ne 0 ]; then
  error "Build failed!"
  exit $BUILD_RESULT
fi

cat <<EOF
===== Build success! ======

Tests will now run in interactive terminal mode.

Press Ctrl-C now to interrupt them. Afterwards, you can
run bash inside the container by running the following:

  docker run -i -t fontknife bash

To run an interactive Python interpreter inside the container
directly, run the following:

  docker run -i -t fontknife python

===== Running Tests =======
EOF

docker run -i -t fontknife
