# Docker for a Python 3.8 Test Shim

tl;dr
1. 3.8 causes the most problems for this project
2. If you're running tests, you probably already have docker with Python images downloaded
3. We can use those to test on 3.8 without breaking anything else on your system

## Usage

### Who Should Use This?

Mostly the following:

1. People who don't want to install [PDM](https://pdm.fming.dev/latest/)
2. Debian users, who are [advised against using PPAs by the official doc](https://wiki.debian.org/DontBreakDebian)
3. People who don't want to risk breaking their system Python install

### How Do I Use This?

First, makes you're capable of running Docker containers. For a *NIX system (mac, Linux, etc),
the steps will be roughly as follows:

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

For their own projects, most people should also consider one of the following:

* [PDM](https://pdm.fming.dev/latest/) for cross-platform Python interpreter version management
* [The deadsnakes PPA](https://github.com/deadsnakes) for Linux users on Debian / Ubuntu
  derivatives (Linux Mint, Pop!_OS, BunsenLabs, etc)

#### Early Adopters

Try [rye](https://github.com/mitsuhiko/rye). I've heard good things!


#### GitHub Actions Enthusiasts

If you want something which acts like a local version of GitHub actions,
I've found two options:

* [act](https://github.com/nektos/act), a golang utility with some rough edges.
* [Whatever Red Hat is doing](https://www.redhat.com/en/blog/testing-github-actions-locally),
  a pair of JS-based repos which seem to be pretty heavy. I haven't tried this one.