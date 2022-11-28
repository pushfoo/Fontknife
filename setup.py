from setuptools import setup, find_packages
from pathlib import Path

CWD = Path(__file__).parent
long_description = (CWD / 'README.md').read_text()


setup(
    name='fontknife',
    version='0.1.2',
    author='pushfoo',
    url='https://github.com/pushfoo/fontknife',
    description="Rasterize only the glyphs you need.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['pillow>=9.3,<10'],
    packages=find_packages(include=['fontknife', 'fontknife.*']),
    entry_points={
        "console_scripts": [
            "fontknife=fontknife.commands.__main__:main",
        ]
    },
    requires_python='>=3.7',
    tests_require=['pytest>=7.1,<8'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Fonts",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Arcade",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Software Development :: Libraries",
    ]
)
