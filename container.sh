#!/bin/bash
# Helper script to kick off install & run tests.

# This is run separately from the main container build because it can
# break before the test suite under some Python versions.
python -m pip install -e .[dev]
pytest tests
