import sys
import click
# import re
import os
# import fnmatch
from .gpm import GPM
from . import version, APPLICATIONS, EXPORT_URL
from .helpers import generate_samples, write_file_run_bcl2fastq, write_file_run_cellranger_mkfastq, copyfromdata, show_tree, move_igv, tar_exports, export_empty_folder
# from pathlib import Path
import datetime
# import collections
import glob
import subprocess

helps = {"raw": 'Enter the path to the directory for the BCL raw data, e.g. 210903_NB501289_0495_AHLLHTBGXJ',
         "app": "Choose the application ("+" ".join(APPLICATIONS)+")",
         "name": "Enter the name of the new project in the format of YYMMDD_ProviderSurname_PISurname_Institute_Application",
         "base": "Define the base directory of the project",
         "demultiplex_output": "Define the output directory for bcl2fastq. This folder should have the same name as run folder.",
         "fastq": "Define the directory to the FASTQ files."}

###################################################################
## Main function
###################################################################
@click.group()
@click.version_option(version)
def main():
    """Genomic Project Manager is a project management CLI for bioinformatic workflows of IZKF Genomic Facility.
       Contact: ckuo@ukaachen.de 
    """
    pass

###################################################################
## demultiplex
###################################################################
@main.command()
@click.option('-r', '--raw', help=helps["raw"], required=True)
@click.option('-o', '--output', help=helps["demultiplex_output"], required=True)
def demultiplex(raw, output):
    """A wrapper of bcl2fastq programm and cellranger mkfastq for demultiplexing."""
    # if not output:
    #     rawname = os.path.basename(raw)
    #     output = os.path.join("/fastq", rawname)

    if not os.path.exists(output):
        os.makedirs(output)
    else:
        click.echo("The defined output directory exists.")
        click.echo(output)
        sys.exit()

    write_file_run_bcl2fastq(raw, output)
    write_file_run_cellranger_mkfastq(raw, output)
    copyfromdata("bcl2fastq/samplesheet.csv", output)

    show_tree(output)
    click.echo()
    click.echo(click.style("Next steps:", fg='bright_green'))
    click.echo("1. Modify samplesheet.csv with the proper information. Please add Sample_Project with the correct format (YYMMDD_Provider_PI_Institute_App).")
    click.echo("2. Check and modify run_bcl2fastq.sh (bulk sequencing) or run_cellranger.sh (single cell sequencing)")
    click.echo("3. Run run_bcl2fastq.sh (bulk sequencing) or run_cellranger.sh (single cell sequencing) with the command below: (Recommend to run it in screen session)")
    click.echo("\tbash run_bcl2fastq.sh")
    click.echo("\tbash run_cellranger.sh")


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
    click.echo("2. Check the command in nfcore/run_nfcore_"+app.lower()+".sh")
    click.echo("3. Run the command in screen session with bash nfcore/run_nfcore_"+app.lower()+".sh")
 
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
## analysis
###################################################################
@main.command()
@click.argument('config_file')
def analysis(config_file):
    """Prepare the Rmd templates for basic analysis"""
    path_config = os.path.join(os.getcwd(), config_file)
    gpm = GPM(load_config=path_config, seqdate=None, application=None, 
              provider=None, piname=None, institute=None, fastq=None, name=None)
    gpm.analysis()
    gpm.show_tree()

###################################################################
## export
###################################################################
@main.command()
@click.argument('export_dir')
@click.option('-config', default="", show_default=True, help="Define the config.ini file of an existed project. If FALSE, -user needs to be defined to create an empty export folder.")
@click.option('-user', default="user", show_default=True, help="Define the user name for creating an empty export folder.")
@click.option('-analysis', default="", show_default=True, help="Define the source of analysis folder for soft linking.")
@click.option('-bcl', default="", show_default=True, help="Define the source of BCL folder for soft linking.")
def export(export_dir, config, user, analysis, bcl):
    """Export the raw data, processed data and reports to the export directory by creating soft links without moving around the big files."""
    if os.path.isfile(config):
        gpm = GPM(load_config=config, seqdate=None, application=None, 
                provider=None, piname=None, institute=None, fastq=None, name=None)
        gpm.export(export_dir)
        gpm.add_htaccess(export_dir)
        gpm.create_user(export_dir)
    else:
        export_empty_folder(EXPORT_URL, export_dir, config, user)
    if analysis:
        # if not os.path.exists(os.path.join(export_dir,"analysis")):
        #     os.makedirs(os.path.join(export_dir,"analysis"))
        os.symlink(analysis, os.path.join(export_dir,"analysis"), target_is_directory=True)
    if bcl:
        os.symlink(bcl, os.path.join(export_dir,"1_Raw_data", "BCL"), target_is_directory=True)

    

###################################################################
## tar export with symlinks
###################################################################
@main.command()
@click.argument('export_dir')
@click.option('--no/--no-behaviour', default=False, show_default=True, help="List the behaviours of the command without actually tarring them.")
def tar_export(export_dir, no):
    """Tar the sub folders under the export directory with symlinks, except compressed_tar folder."""
    tar_exports(export_dir, no)

###################################################################
## clean the folders
###################################################################
@main.command()
@click.argument('targetfolder')
@click.option('--no/--no-behaviour', default=False, show_default=True, help="List the behaviours of the command without actually removing them.")
def clean(targetfolder, no):
    """Clean the temporary files and folders in target folders which shouldn't be archived or backup, such as *fastq.gz, nf-core work folder and result folder."""
    tmp_patterns = ["*.fastq.gz",
                    "*/*.fastq.gz",
                    "nfcore/work"]
    for p in tmp_patterns:
        target_pattern = targetfolder+"/"+p
        listfiles = glob.glob(target_pattern)
        if listfiles:
            click.echo("Clean "+target_pattern)
            if not no:
                result = subprocess.run(["rm", "-fr", target_pattern], stderr=subprocess.PIPE, text=True)
                click.echo(result.stderr)
    

###################################################################
## igv session for nf-core ChIP-Seq
###################################################################
@main.command()
@click.argument('igv_session')
def igv(igv_session):
    """Make IGV session accessible via ssh -X by moving the target igv_session.xml to ../../ and remove ../.. in all the paths. This is mainly for nf-core chipseq pipeline."""
    move_igv(igv_session)

if __name__ == '__main__':
    main()