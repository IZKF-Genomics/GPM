import sys
import click
import re
import os
import fnmatch
from .gpm import GPM
from . import version, APPLICATIONS
from .helpers import generate_samples, write_file_run_bcl2fastq, copyfromdata, show_tree, move_igv
from pathlib import Path
import datetime
import collections


helps = {"raw": 'Enter the path to the directory for the BCL raw data, e.g. 210903_NB501289_0495_AHLLHTBGXJ',
         "app": "Choose the application ("+" ".join(APPLICATIONS)+")",
         "name": "Enter the name of the new project in the format of YYMMDD_ProviderSurname_PISurname_Institute_Application",
         "base": "Define the base directory of the project",
         "bcl2fastq_output": "Define the output directory for bcl2fastq. This folder should have the same name as run folder.",
         "fastq": "Define the directory to the FASTQ files."}

###################################################################
## Main function
###################################################################
@click.group()
@click.version_option(version)
def main():
    """Genomic Project Manager is a project management CLI for bioinformatic workflows of IZKF Genomic Core Facility.
       Contact: ckuo@ukaachen.de 
    """
    pass

###################################################################
## bcl2fastq: Demultiplexing
###################################################################
@main.command()
@click.option('-r', '--raw', help=helps["raw"], required=True)
@click.option('-o', '--output', help=helps["bcl2fastq_output"], required=True)
def bcl2fastq(raw, output):
    """A wrapper of bcl2fastq programm for demultiplexing."""
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
    copyfromdata("bcl2fastq/samplesheet.csv", output)

    show_tree(output)
    click.echo()
    click.echo(click.style("Next steps:", fg='bright_green'))
    click.echo("1. Modify samplesheet.csv with the proper information. Please add Sample_Project with the correct format (YYMMDD_Provider_PI_Institute_App).")
    click.echo("2. Modify run_bcl2fastq.sh especially --use-bases-mask.")
    click.echo("3. Run run_bcl2fastq.sh with the command below:")
    click.echo("\tnohup bash run_bcl2fastq.sh &")


###################################################################
## init: Initiate a new project for analyses
###################################################################
@main.command()
@click.option('-fq', '--fastq', help=helps["fastq"], required=True)
@click.option('-n', '--name', help=helps["name"], required=True)
def init(fastq, name):
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
    gpm = GPM(seqdate=seqdate, application=app, 
                      provider=provider, piname=piname, institute=institute,
                      fastq=fastq, name=name)
    
    gpm.show_config()
    gpm.show_tree()

    # Todo 
    click.echo()
    click.echo(click.style("Next steps:", fg='bright_green'))
    click.echo("1. Generate the sample sheet under nfcore directory. Ref: gpm samplesheet")
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
    """Generate sample sheet for nf-core RNAseq pipeline."""
    generate_samples(st, fastq_dir, samplesheet, 
                     r1, r2, se, sn, sd, si)


###################################################################
## igv session
###################################################################
@main.command()
@click.argument('igv_session')
def igv(igv_session):
    """Make IGV session accessible via ssh -X by moving the target igv_session.xml to ../../ and remove ../.. in all the paths. This is mainly for nf-core chipseq pipeline."""
    move_igv(igv_session)

###################################################################
## export
###################################################################
@main.command()
@click.argument('config_file')
@click.argument('export_dir')
@click.option('--tar', is_flag=True, help="If --tar is set, three seperate tar files will be generated for 1_Raw_data, 2_Processed_data and 3_Reports.")
def export(config_file, export_dir, tar):
    """Export the raw data, processed data and reports to the export directory by creating soft links without moving around the big files."""
    gpm = GPM(load_config=config_file,
                      seqdate=None, application=None, 
                      provider=None, piname=None, institute=None,
                      fastq=None, name=None)

    gpm.export(export_dir, tar)

if __name__ == '__main__':
    main()