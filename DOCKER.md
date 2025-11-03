# I Want To Test on Python $VERSION!

**TL;DR:** Run `./test_in_docker.sh 3.9` and look for red

To specify a version, you can manually configure it via Docker's `--build-arg` option like so:

```console
$ docker build -f tests.Dockerfile --build-arg="PY_VERSION=3.9" -t fontknife:3.9 .
```

However, the helper script is shorter.

## Usage

### Who's the Target Audience

[DontBreakDebian]: https://wiki.debian.org/DontBreakDebian

1. Debian users (The official [DontBreakDebian][] page warns against using PPAs)
2. Anyone else scared of breaking their Python install
3. Container and reproducibility enthusiasts

### How Do I Use This?

First, makes you're capable of running Docker containers. For a *NIX system (mac, Linux, etc),
the steps will be roughly as follows:

1. `cd` into the project root directory
2. Read `test_in_docker.sh` to make sure you understand it
3. Run `sudo ./test_in_docker.sh` and watch the output

## I don't like Docker!

That's okay. Keep reading.

### Cross-platform Options

[PDM]: https://pdm.fming.dev/latest/
[pyenv]: https://github.com/pyenv/pyenv
[rye]: https://github.com/pyenv/pyenv

For cross-platform Python interpreter version management, consider:

* [PDM][] for both Python and package installation
* [rye][] for a modern take on handling both Python and package installation
* [pyenv][] if you want other Python versions but want to keep plain old `pip`

### Linux Options

[deadsnakes PPA]: https://github.com/deadsnakes

> [!WARNING]
> The Debian wiki's [DontBreakDebian][] page warns against PPAs like this.

The [deadsnakes PPA][] is available for Linux users on Debian and Ubuntu
derivatives (Linux Mint, Pop!_OS, CrunchBang++, BunsenLabs, etc).

### GitHub Actions Enthusiasts

[act]: https://github.com/nektos/act
[Red Hat is doing]: https://www.redhat.com/en/blog/testing-github-actions-locally

If you want something which acts like a local version of GitHub actions,
I've found two options:

* [act][], a golang utility with some rough edges
* Whatever [Red Hat is doing][] with a heavy-looking pair of JS-based repos
  (haven't tried this)
