from setuptools import find_packages, setup
from gpm import version

setup(
    name="gpm",
    version=version,
    description = "Genomic Project Manager for automatizing the bioinformatic workflow in IZKF Genomic Core Facility.",
    long_description = "This command line tool is designed to simplifiy and automatize the bioinformatic workflow in IZKF Genomic Core Facility.",
    platforms = ["Linux"],
    author="Chao-Chung Kuo",
    author_email="chao-chung.kuo@rwth-aachen.de",
    url="https://github.com/IZKF-Genomics/gpm",
    license = "MIT",
    packages = find_packages(),
    # packages=['mypkg'],
    package_dir = {'gpm': 'gpm'},
    package_data = {'gpm': ['data/*', 'data/bcl2fastq/*', 'data/nfcore/*', 'data/export/*', 'data/analysis/*']},
    py_modules = ['gpm'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        gpm=gpm.main:main
    ''',
)