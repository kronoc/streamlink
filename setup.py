#!/usr/bin/env python
from os import environ, path
from sys import argv, exit, version_info
from textwrap import dedent

from setuptools import setup

import versioneer


def format_msg(text, *args, **kwargs):
    return dedent(text).strip(" \n").format(*args, **kwargs)


CURRENT_PYTHON = version_info[:2]
REQUIRED_PYTHON = (3, 6)

# This check and everything above must remain compatible with older Python versions
if CURRENT_PYTHON < REQUIRED_PYTHON:
    exit(format_msg("""
        ========================================================
                       Unsupported Python version
        ========================================================
        This version of Streamlink requires at least Python {}.{},
        but you're trying to install it on Python {}.{}.

        This may be because you are using a version of pip that
        doesn't understand the python_requires classifier.
        Make sure you have pip >= 9.0 and setuptools >= 24.2
    """, *(REQUIRED_PYTHON + CURRENT_PYTHON)))

# Explicitly disable running tests via setuptools
if "test" in argv:
    exit(format_msg("""
        Running `python setup.py test` has been deprecated since setuptools 41.5.0.
        Streamlink requires pytest for collecting and running tests, via one of these commands:
        `pytest` or `python -m pytest` (see the pytest docs for more infos about this)
    """))


deps = [
    "requests>=2.26.0,<3.0",
    "isodate",
    "lxml>=4.6.4,<5.0",
    "websocket-client>=1.2.1,<2.0",
    # Support for SOCKS proxies
    "PySocks!=1.5.7,>=1.5.6",
]

# for encrypted streams
if environ.get("STREAMLINK_USE_PYCRYPTO"):
    deps.append("pycrypto")
else:
    # this version of pycryptodome is known to work and has a Windows wheel for py2.7, py3.3-3.6
    deps.append("pycryptodome>=3.4.3,<4")

# for localization
if environ.get("STREAMLINK_USE_PYCOUNTRY"):
    deps.append("pycountry")
else:
    deps.append("iso-639")
    deps.append("iso3166")


def is_wheel_for_windows():
    if "bdist_wheel" in argv:
        names = ["win32", "win-amd64", "cygwin"]
        length = len(argv)
        for pos in range(argv.index("bdist_wheel") + 1, length):
            if argv[pos] == "--plat-name" and pos + 1 < length:
                return argv[pos + 1] in names
            elif argv[pos][:12] == "--plat-name=":
                return argv[pos][12:] in names
    return False


entry_points = {
    "console_scripts": ["streamlink=streamlink_cli.main:main"]
}

if is_wheel_for_windows():
    entry_points["gui_scripts"] = ["streamlinkw=streamlink_cli.main:main"]


# optional data files
data_files = [
    # shell completions
    #  requires pre-built completion files via shtab (dev-requirements.txt)
    #  `./script/build-shell-completions.sh`
    ("share/bash-completion/completions", ["build/shtab/bash/streamlink"]),
    ("share/zsh/site-functions", ["build/shtab/zsh/_streamlink"]),
    # man page
    #  requires pre-built man page file via sphinx (docs-requirements.txt)
    #  `make --directory=docs clean man`
    ("share/man/man1", ["docs/_build/man/streamlink.1"])
]
data_files = [
    (destdir, [file for file in srcfiles if path.exists(file)])
    for destdir, srcfiles in data_files
]


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=deps,
    entry_points=entry_points,
    data_files=data_files,
)
