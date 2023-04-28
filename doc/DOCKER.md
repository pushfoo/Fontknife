# Docker for a Python 3.8 Test Shim

tl;dr test on the most troublesome supported Python version inside a Docker container

## Usage

### Who Should Use This?

Mostly the following:

1. Debian users, which [advises not using PPAs](https://wiki.debian.org/DontBreakDebian)
2. People who don't want to risk breaking their system Python install
3. Repeatable build enthusiasts

### How do I Use This?

1. Be running on a *NIX system (mac, Linux, etc) with Docker installed
2. `cd` into the project root directory
3. Read `test_python38.sh` to make sure you understand it
4. Run `chmod +x test_python38.sh`
5. Make sure your internet connection is good
6. Run `sudo ./test_python38.sh` and watch the output

## Why this instead of $TOOL?

1. 3.8 is the only Python version
   [causing enough trouble for a special approach to be worth it](https://xkcd.com/1205/)
2. My current Linux distro doesn't package Python 3.8 in the default repos
3. I didn't want to configure additional PPAs

### The alternatives better for...

#### Most people

For their own projects, most people should als consider one of the following:

* [PDM](https://pdm.fming.dev/latest/) for cross-platform Python interpreter version management
* [The deadsnakes PPA](https://github.com/deadsnakes) for Linux users on Debian / Ubuntu
  derivatives (Linux Mint, Pop!_OS, BunsenLabs, etc)

#### Early Adopters

Try [rye](https://github.com/mitsuhiko/rye). I've heard good things!


#### GitHub Actions Enthusiasts

If you want something which acts like a local version of GitHub actions,
I've found two options but haven't tried them:

* [act](https://github.com/nektos/act), a well-documented golang utility
* [Whatever Red Hat is doing](https://www.redhat.com/en/blog/testing-github-actions-locally),
  a pair of JS-based repos which seem to be pretty heavy