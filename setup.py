# coding: utf-8

"""Setup file for PyPI"""

from setuptools import setup, find_packages
from setuptools.extension import Extension
from distutils.extension import Extension
from Cython.Build import cythonize
from codecs import open
from os import path
import glob
import re
import sys

here = path.abspath(path.dirname("__file__"))

with open(path.join(here, "DESCRIPTION.md"), encoding="utf-8") as description:
    long_description = description.read()

version = {}
with open(path.join(here, "Mikado", "version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

if version is None:
    print("No version found, exiting", file=sys.stderr)
    sys.exit(1)

if sys.version_info.major != 3:
    raise EnvironmentError("""Mikado is a pipeline specifically programmed for python3,
    and is not compatible with Python2. Please upgrade your python before proceeding!""")

extensions = [Extension("Mikado.utilities.overlap",
                        sources=[path.join("Mikado", "utilities", "overlap.pyx")]),
              Extension("Mikado.scales.f1",
                        sources=[path.join("Mikado", "scales", "f1.pyx")]),
              Extension("Mikado.scales.contrast",
                        sources=[path.join("Mikado", "scales", "contrast.pyx")]),
              Extension("Mikado.utilities.intervaltree",
                        sources=[path.join("Mikado", "utilities", "intervaltree.pyx")])]

setup(
    name="Mikado",
    version=version,
    description="A Python3 annotation program to select the best gene model in each locus",
    long_description=long_description,
    url="https://github.com/EI-CoreBioinformatics/mikado",
    author="Luca Venturini",
    author_email="lucventurini@gmail.com",
    license="LGPL3",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=[
        "Development Status :: 5 - Production",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Framework :: Pytest",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        'Programming Language :: Python :: 3.7'
    ],
    ext_modules=cythonize(extensions, compiler_directives = {"language_level": "3"}),
    zip_safe=False,
    keywords="rna-seq annotation genomics transcriptomics",
    packages=find_packages(),
    # scripts=glob.glob("bin/*.py") + glob.glob("util/*.py"),
    scripts=glob.glob("util/*.py"),
    entry_points={"console_scripts": ["mikado = Mikado:main",
                                      "daijin = Mikado.daijin:main",
                                      ]},
    install_requires=[line.rstrip() for line in open("requirements.txt", "rt")],
    extras_require={
        "postgresql": ["psycopg2"],
        "mysql": ["mysqlclient>=1.3.6"],
        "bam": ["pysam>=0.8"]
    },
    test_suite="nose2.collector.collector",
    package_data={
        "Mikado.configuration":
            glob.glob("Mikado/configuration/*json") + glob.glob("Mikado/configuration/*yaml"),
        "Mikado.configuration.scoring_files":
            glob.glob("Mikado/configuration/scoring_files/*"),
        "Mikado":
            glob.glob(path.join("Mikado", "daijin", "*yaml")) +
            glob.glob("Mikado/daijin/*json") + \
            glob.glob("Mikado/daijin/*snakefile"),
        "Mikado.utilities.overlap": [path.join("Mikado", "utilities", "overlap.pxd")],
        "Mikado.utilities.intervaltree": [path.join("Mikado", "utilities", "intervaltree.pxd")],
        },
    include_package_data=True
    # data_files=[
    #     ("Mikado/configuration",
    #      glob.glob("Mikado/configuration/*json") + glob.glob("Mikado/configuration/*yaml"))],

)
