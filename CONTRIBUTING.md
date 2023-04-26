# Contributing

## Overview

1. File issues or pull requests on this GitHub repo.
2. `pip install -e .[dev]` to run a developer install
3. If you get an error about `pyproject.toml`, run `pip install --upgrade pip`
   and retry
4. Run `pytest tests` to tests after making changes
5. Try to add tests when appropriate
6. Be excellent to each other

## Developer Install

First, [create a virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments)
& activate it.

Then, run the following to set up development dependencies:

```console
pip install -e .[dev]
```

If you see an error message like the following...

```commandline
ERROR: File "setup.py" not found. Directory cannot be installed in editable mode: /home/user/Projects/octofont3
(A "pyproject.toml" file was found, but editable mode currently requires a setup.py based build.)
```

You need to upgrade your pip / setuptools, or your preferred package manager. It
needs to be recent enough to support [PEP-660](https://peps.python.org/pep-0660/).

For `pip`, upgrade to at least [version 21.3](https://pip.pypa.io/en/stable/news/#v21-3):

```commandline
pip install --upgrade pip
```

Afterward, you should be able to re-run the first install command.


## Running Tests

Tests are run with pytest as follows:

```commandline
pytest tests
```

If you are making changes such as adding or changing features, try to add or update the
unit tests if possible. It's also ok to ask for help with this!
