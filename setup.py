from setuptools import setup, find_packages

setup(
    name='octofont3',
    version='0.1',
    install_requires=['pillow'],
    packages=find_packages(include=['octofont3', 'octofont3.*']),
    entry_points={
        "console_scripts": [
            "textfont-to-octo=octofont3.textfont_to_octo:main",
            'create-textfont=octofont3.create_textfont:main'
        ]
    }
)