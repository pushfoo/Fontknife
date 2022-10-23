from setuptools import setup, find_packages

setup(
    name='octofont3',
    version='0.1',
    install_requires=['pillow'],
    packages=find_packages(include=['octofont3', 'octofont3.*']),
    entry_points={
        "console_scripts": [
            "octofont3=octofont3.commands.__main__:main",
        ]
    },
    tests_require=['pytest~=7.*']
)