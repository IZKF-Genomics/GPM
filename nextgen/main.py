import sys
import click
import re
import os
import fnmatch
from .nextgen import Nextgen
from . import version, APPLICATIONS
from .helpers import generate_samples, write_file_run_bcl2fastq, copyfromdata
from pathlib import Path
import datetime
import collections


helps = {"raw": 'Enter the path to the directory for the BCL raw data, e.g. 210903_NB501289_0495_AHLLHTBGXJ',
         "app": "Choose the application ("+" ".join(APPLICATIONS)+")",
         "name": "Enter the name of the new project in the format of YYMMDD_ProviderSurname_PISurname_Institute_Application",
         "base": "Define the base directory of the project",
         "bcl2fastq_output": "Define the output directory for bcl2fastq. By default, the folder with the same name as run folder will be generated under /fastq"}

###################################################################
## Main function
###################################################################
@click.group()
@click.version_option(version)
def main():
    """A project management CLI for bioinformatic workflows."""
    pass

###################################################################
## bcl2fastq
###################################################################
@main.command()
@click.option('-r', '--raw', help=helps["raw"], required=True)
@click.option('-o', '--output', help=helps["bcl2fastq_output"], default=None)
def bcl2fastq(raw, output):
    """A wrapper of bcl2fastq programm."""
    if not output:
        rawname = os.path.basename(raw)
        output = os.path.join("/fastq", rawname)

    if not os.path.exists(output):
        os.makedirs(output)
    else:
        click.echo("The defined output directory exists.")
        click.echo(output)
        sys.exit()
    
    write_file_run_bcl2fastq(raw, output)
    copyfromdata("bcl2fastq_samplesheet.csv", output)

###################################################################
## init
###################################################################
@main.command()
@click.option('-r', '--raw', help=helps["raw"], required=True)
@click.option('-n', '--name', help=helps["name"], required=True)
def init(raw, name):
    """Initiate a new project."""
    split_name = name.split("_")
    # seqdate
    seqdate = split_name[0]
    try:
        datetime.datetime.strptime(seqdate, "%y%m%d")
    except ValueError:
        click.echo("This is the incorrect date string format. It should be YYMMDD")
        sys.exit()
    # app
    app = split_name[4]
    if app not in APPLICATIONS:
        click.echo("Please type exactly the app name in the list: "+" ".join(APPLICATIONS))
        sys.exit()
    
    # surnames
    provider = split_name[1].capitalize()
    piname = split_name[2].capitalize()
    institute = split_name[3]
    nextgen = Nextgen(seqdate=seqdate, application=app, 
                      provider=provider, piname=piname, institute=institute,
                      bcl_dir=raw, name=name)
    
    nextgen.show_config()
    nextgen.show_tree()

    nextgen.write_file_run_bcl2fastq()
    # Todo 
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