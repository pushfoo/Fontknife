from setuptools import setup, find_packages

setup(
    name='fontknife',
    version='0.1',
    install_requires=['pillow'],
    packages=find_packages(include=['fontknife', 'fontknife.*']),
    entry_points={
        "console_scripts": [
            "fontknife=fontknife.commands.__main__:main",
        ]
    },
    tests_require=['pytest>=7,<8']
)