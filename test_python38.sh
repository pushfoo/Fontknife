#!/bin/bash

echo "== Python 3.8 on Docker Wrapper Script =="
echo "   (See doc/DOCKER.md for more info)"
echo

# Command for building the image
BUILD_CMD="docker build -f python38.Dockerfile -t fontknife ."


function exit_error() {
  # Print the message, return to the original dir, and exit
  local message="$1"

  echo "ERROR: $message"
  exit 1
}

if [[ "$(uname -s)" == "Linux" && "$EUID" -ne 0 ]]; then
  exit_error "Docker requires root on Linux!"
fi

# If the build command returns a fail code
if ! $BUILD_CMD; then
  exit_error "Build failed!"
else
  echo "===== Build success! ======"
  echo
  echo "To get a commandline inside the container, run the following:"
  echo "  docker run -i -t fontknife bash"
  echo
  echo "To run an interactive Python interpreter inside the container, run the following:"
  echo "  docker run -i -t fontknife python"
  echo
  echo "===== Running Tests ======="
  echo
  docker run -i -t fontknife
fi
