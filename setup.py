from setuptools import find_packages, setup
from nextgen import version

setup(
    name="nextgen",
    version=version,
    description = "Automatizing the bioinformatic workflow in IZKF Genomic Core Facility.",
    long_description = "This command line tool is designed to simplifiy and automatize the bioinformatic workflow in IZKF Genomic Core Facility.",
    platforms = ["Linux"],
    author="Chao-Chung Kuo",
    author_email="chao-chung.kuo@rwth-aachen.de",
    url="https://github.com/IZKF-Genomics/nextgen",
    license = "MIT",
    packages = find_packages(),
    # packages=['mypkg'],
    package_dir = {'nextgen': 'nextgen'},
    package_data = {'nextgen': ['data/*', 'data/bcl2fastq/*', 'data/nfcore/*', 'data/export/*']},
    py_modules = ['nextgen'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        nextgen=nextgen.main:main
    ''',
)