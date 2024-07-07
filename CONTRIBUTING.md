# Contributing

## Overview

[fork]: https://github.com/pushfoo/fontknife/fork
[clone]: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
[virtual environment]: https://docs.python.org/3/library/venv.html#creating-virtual-environments

1. Above all else, be excellent to each other
2. File issues or pull requests on this GitHub repo
3. Follow standard [fork][], [clone][], and [virtual environment][] practices

## Developer install

1. [Fork][fork] a copy onto your account
2. [Clone][clone] the repo onto your system
3. `cd Fontknife` or the name of your fork
4. Create a [virtual environment] and activate it
5. Update to the latest `pip` with `pip install --upgrade pip`
6. `pip install -e .[dev,docs]`

If running `fontknife` emits help text, we're good to go.

### Troubleshooting

**TL;DR:** Make sure you ran  `pip install --upgrade pip`

[PEP-660]: https://peps.python.org/pep-0660/
[version 21.3]: https://pip.pypa.io/en/stable/news/#v21-3

Your `pip` and `setuptools` need be recent enough to support needs to be
recent enough to support [PEP-660][].

If you run `pip --version`, it should be at least [version 21.3][]. If it
isn't, then you might encounter  one of the errors below. In both cases,
the solution is the same:

```console
pip install --upgrade pip
```

#### An Error About `pyproject.toml`

If it says it can't parse it or similar, `pip install --upgrade pip`.

#### An Error About `setup.py`

If you see an error message like the following...

```commandline
ERROR: File "setup.py" not found. Directory cannot be installed in editable mode: /home/user/Projects/octofont3
(A "pyproject.toml" file was found, but editable mode currently requires a setup.py based build.)
```

Then `pip install --upgrade pip`.

## Making Changes

[File an issue]: https://github.com/pushfoo/Fontknife/issues
[tests]:  https://github.com/pushfoo/Fontknife/tree/main/tests
[Make a pull request]: https://github.com/pushfoo/Fontknife/pulls

1. [File an issue][]
2. Discuss as necessary if the work isn't trivial
3. In addition to writing code, try to add or update any tests
   1. Look in the [`Fontknife/tests`][tests] folder to find them
   2. Run them with either of the following:
      * `pytest tests`
      * If you have Docker, you can also use one of the following:
        * Easy mode: `test_in_docker.sh 3.8` or any Python version other than 3.8
        * Hard mode: `docker build` with a `--build-arg='PYTHON_VERSION=3.8`
4. `git push` your code to your fork
5. [Make a pull request][]

For information on Docker, see [DOCKER.md](DOCKER.md).
