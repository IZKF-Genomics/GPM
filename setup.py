from setuptools import find_packages, setup
from gpm import version
from os import path, getenv, makedirs, listdir, environ
import shutil

###################################################################################################
# Creating Data Path
###################################################################################################

# if the environment variable is set, use it; otherwise use the home directory as a default
if environ.get('GPMDATA'):
    gpm_data_location = path.expanduser(getenv("GPMDATA"))
else:
    gpm_data_location = path.expanduser(path.join(getenv("HOME"), "gpmdata"))
print("GPMDATA folder: "+gpm_data_location)

# Creating Data Path
if not path.exists(gpm_data_location):
    makedirs(gpm_data_location)
# GPM Configs
config_dir = path.join(path.dirname(__file__), "gpm/configs")
for file in listdir(config_dir):
    fn = path.basename(file)
    shutil.copyfile(path.join(config_dir,fn),
                    path.join(gpm_data_location,fn))
    # User defined Configs
    # userconfig = open(path.join(gpm_data_location,fn+".user"), "w")
    # with open(path.join(config_dir,fn)) as f1:
    #     for line in f1.readlines():
    #         print("# "+line, file=userconfig, end="")
    # userconfig.close()

###################################################################################################
# Setup function
###################################################################################################

setup(
    name="gpm",
    version=version,
    description = "Genomic Project Manager for automatizing the bioinformatic workflow in IZKF Genomic Facility.",
    long_description = "This command line tool is designed to simplifiy and automatize the bioinformatic workflow in IZKF Genomic Facility.",
    platforms = ["Linux"],
    author="Chao-Chung Kuo",
    author_email="chao-chung.kuo@rwth-aachen.de",
    url="https://github.com/IZKF-Genomics/gpm",
    license = "MIT",
    packages = find_packages(),
    # packages=['mypkg'],
    package_dir = {'gpm': 'gpm'},
    package_data = {'gpm': ['data/*', 'data/demultiplex/bcl2fastq/*', 'data/nfcore/*', 'data/demultiplex/cellranger/*',
                            'data/export/*', 'data/analysis/*', 'data/analysis/cellranger/*','configs/*']},
    py_modules = ['gpm'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        gpm=gpm.main:main
    ''',
)

