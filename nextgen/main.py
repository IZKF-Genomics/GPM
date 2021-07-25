import sys
import click
import re
import os
import fnmatch
from .nextgen import Nextgen
from . import version, APPLICATIONS
from .helpers import DisplayablePath, generate_samples
from pathlib import Path
import datetime
import collections


helps = {"seqdate": 'Enter the date for sequencing (YYYY-MM-DD, such as 2021-02-28)',
         "app": "Choose the application ("+" ".join(APPLICATIONS)+")",
         "pi": "Enter the surname of the PI",
         "fastq": "Define the path to the fastq files",
         "base": "Define the base directory of the project"}


def show_tree(base):
    click.echo(click.style("The current status of the project directory:", fg='bright_green'))
    paths = DisplayablePath.make_tree(Path(base))
    for path in paths:
        click.echo(path.displayable())

###################################################################
## Main function
###################################################################
@click.group()
@click.version_option(version)
def main():
    """A project management CLI for bioinformatic workflows."""
    pass

###################################################################
## init
###################################################################
@main.command()
@click.option('--seqdate', default=None, help=helps["seqdate"])
@click.option('--app', default=None, help=helps["app"])
@click.option('--pi', default=None, help=helps["pi"])
def init(seqdate, app, pi):
    """Initiate a new project."""
    # seqdate
    if not seqdate:
        click.echo('> '+helps["seqdate"]+":")
        seqdate = input()
    try:
        datetime.datetime.strptime(seqdate, "%Y-%m-%d")
    except ValueError:
        click.echo("This is the incorrect date string format. It should be YYYY-MM-DD")
        sys.exit()
    # app
    if not app:
        click.echo('> Choose the application by entering the number:')
        for i,ap in enumerate(APPLICATIONS):
            click.echo("\t".join(['\t', str(i+1), ap]))
        app = input()
        try:
            app = APPLICATIONS[int(app)-1]
        except:
            click.echo("Error. Please enter a number between 1 and "+str(len(APPLICATIONS)))
            sys.exit()
    else:
        if app not in APPLICATIONS:
            click.echo("Please type exactly the app name in the list: "+" ".join(APPLICATIONS))
            sys.exit()
    
    # PI
    if not pi:
        click.echo('> '+helps["pi"]+":")
        PI = input().capitalize()
    else:
        PI = pi.capitalize()
    
    nextgen = Nextgen(seqdate, app, PI)
    show_tree(nextgen.base)
    
    click.echo()
    click.echo(click.style("Next steps:", fg='bright_green'))
    click.echo("1. Generate the sample sheet under nfcore directory. Ref: nextgen samplesheet")
    click.echo("2. Check the nfcore/nextflow.config file.")
    click.echo("3. Finish the command in nfcore/run_nfcore_"+app.lower()+".sh")
 
#TODO: add reminder for sample sheet and nfcore config

###################################################################
## samplesheet
# help="Define the project folder where the config.ini file ist."
# , help="Folder containing raw FastQ files."
###################################################################
@main.command()
@click.argument('samplesheet')
@click.argument('fastq_dir')
@click.option('-st', default="unstranded", show_default=True, help="Value for 'strandedness' in samplesheet. Must be one of 'unstranded', 'forward', 'reverse'.")
@click.option('-r1', default="_R1_001.fastq.gz", show_default=True, help="File extension for read 1.")
@click.option('-r2', default="_R2_001.fastq.gz", show_default=True, help="File extension for read 2.")
@click.option('-se', default=False, show_default=True, help="Single-end information will be auto-detected but this option forces paired-end FastQ files to be treated as single-end so only read 1 information is included in the samplesheet.")
@click.option('-sn', default=False, show_default=True, help="Whether to further sanitise FastQ file name to get sample id. Used in conjunction with --sanitise_name_delimiter and --sanitise_name_index.")
@click.option('-sd', default="_", show_default=True, help="Delimiter to use to sanitise sample name.")
@click.option('-si', default=1, show_default=True, help="After splitting FastQ file name by --sanitise_name_delimiter all elements before this index (1-based) will be joined to create final sample name.")
def samplesheet(samplesheet, fastq_dir, st, r1, r2, se, 
                     sn, sd, si):
    generate_samples(st, fastq_dir, samplesheet, 
                     r1, r2, se, sn, sd, si)


if __name__ == '__main__':
    main()