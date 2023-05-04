import sys
import click
import configparser
# import re
import os
# import fnmatch
from .gpm import GPM
from . import version
from .helpers import generate_samples, generate_samples_scrna, write_file_run_bcl2fastq, write_file_run_cellranger_mkfastq, write_file_run_cellranger_merge_lanes, copyfromdata, show_tree, move_igv, tar_exports, export_empty_folder, get_gpmconfig, get_size, write_file_run_qc, update_config_with_name, generate_config_file
# from pathlib import Path
import datetime
# import collections
import glob
import subprocess


helps = {"raw": 'Enter the path to the directory for the BCL raw data, e.g. 210903_NB501289_0495_AHLLHTBGXJ',
         "app": "Choose the application ("+" ".join(get_gpmconfig("GPM","APPLICATIONS"))+")",
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
@click.option('-sc', default=False, show_default=True, help="Flag for single-cell sequencing, otherwise bulk sequencing is set as default.")
@click.option('-miseq', default=False, show_default=True, help="Flag for using autamitaclly the fastq presented under the miseq folder")
def demultiplex(raw, output, sc, miseq):
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
    
    # Generate config file in case an export needed without any analysis
    fastq = os.path.join(os.getcwd(), output)
    generate_config_file(fastq, output, raw)

    if sc:
        write_file_run_cellranger_mkfastq(raw, output)
        write_file_run_cellranger_merge_lanes(raw, output)
        copyfromdata("cellranger/samplesheet.csv", output)
        # If MiSeq was used as the sequencer the data is already demultiplexed!
        if miseq:
            write_file_run_qc(raw, output)

    else:
        write_file_run_bcl2fastq(raw, output)
        copyfromdata("bcl2fastq/samplesheet.csv", output)
        if miseq:
            write_file_run_qc(raw, output)

    show_tree(output)
    click.echo()
    click.echo(click.style("Next steps:", fg='bright_green'))
    if miseq:
        click.echo("i. Check and modify run_qc.sh")
        click.echo("ii. Run run_qc.sh with the command below: (Recommend to run it in screen session)")
        click.echo("\tbash run_qc.sh")
        click.echo("iii. In case a re-run of demultiplexing is required:")
            
    click.echo("1. Modify samplesheet.csv with the proper information. Please add Sample_Project with the correct format (YYMMDD_Provider_PI_Institute_App).")
    if sc:
        click.echo("2. Check and modify run_cellranger_mkfastq.sh")
        click.echo("3. Run run_cellranger_mkfastq.sh with the command below: (Recommend to run it in screen session)")
        click.echo("\tbash run_cellranger_mkfastq.sh")
    else:
        click.echo("2. Check and modify run_bcl2fastq.sh")
        click.echo("3. Run run_bcl2fastq.sh with the command below: (Recommend to run it in screen session)")
        click.echo("\tbash run_bcl2fastq.sh")


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
    if app not in get_gpmconfig("GPM","APPLICATIONS"):
        click.echo("Please type exactly the app name in the list: "+" ".join(get_gpmconfig("GPM","APPLICATIONS")))
        sys.exit()
    
    # surnames
    provider = split_name[1].capitalize()
    piname = split_name[2].capitalize()
    institute = split_name[3]
    gpm = GPM(seqdate=seqdate, application=app, 
              provider=provider, piname=piname, institute=institute,
              fastq=fastq, name=name, load_config=False)
    # TODO: add the bcl path to the confidg file (first set and then write!)\
    gpm.add_bcl_to_config()
    gpm.show_config()
    
    if app == "scRNAseq":
        # In the single-cell RNA-seq the samplesheet is generated with the init command
        generate_samples_scrna(fastq_dir=fastq, samplesheet_file=f"./{name}/nfcore/samplesheet.csv")
        gpm.show_tree()
        click.echo()
        click.echo(click.style("Next steps:", fg='bright_green'))
        click.echo("1. Check the command in nfcore/run_nfcore_"+app.lower()+".sh")
        click.echo("2. Run the command in screen session with bash nfcore/run_nfcore_"+app.lower()+".sh")
    elif app == "scVDJseq":
        # In the single-cell VDJ-seq the samplesheet is generated with the init command
        gpm.show_tree()
        click.echo()
        click.echo(click.style("Next steps:", fg='bright_green'))
        click.echo("1. Check the command in cellranger/run_cellranger_scVDJseq.sh")
        click.echo("2. Run the command in screen session with bash cellranger/run_cellranger_scVDJseq.sh")
    else:
        # Todo
        gpm.show_tree()
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
## export_raw
###################################################################
@main.command()
@click.argument('export_dir')
@click.option('-n', '--name', help=helps["name"], required=True)
@click.option('-c','--config', default="config.ini", show_default=True, help="Define the config.ini file of an existed project.")
@click.option('-s', '--symprefix', default="/mnt/nextgen", show_default=True, help="Define the prefix of soft link from web server to computational server.")
@click.option('-multiqc', is_flag=True, default=False, show_default=True, flag_value=True, help="Include multiqc report")
@click.option('-tar', is_flag=True, default=False, show_default=True, flag_value=True, help="tar the export folder")
def export_raw(export_dir, name, config, symprefix, multiqc, tar):
    """Prepare the Rmd templates for basic analysis"""
    # Add the new data to the config file
    Config = configparser.ConfigParser()
    config_path = os.path.join(os.getcwd(),config)
    Config.read(config_path)
    Config = update_config_with_name(name, Config)

    cfgfile = open(config_path, "w")
    Config.write(cfgfile)
    cfgfile.close()

    # Export according to the config file 
    gpm = GPM(load_config=config, seqdate=None, application=None, 
            provider=None, piname=None, institute=None, fastq=None, name=None)
    gpm.export_raw(export_dir, symprefix,  Config["Project"]["Base Path"], Config["Project"]["FASTQ Path"], multiqc, tar )
    gpm.add_htaccess(export_dir)
    gpm.create_user(export_dir)


###################################################################
## export
###################################################################
@main.command()
@click.argument('export_dir')
@click.option('-config', default="", show_default=True, help="Define the config.ini file of an existed project. If FALSE, -user needs to be defined to create an empty export folder.")
@click.option('-user', default="user", show_default=True, help="Define the user name for creating an empty export folder.")
@click.option('-analysis', default="", show_default=True, help="Define the source of analysis folder for soft linking.")
@click.option('-bcl', default="", show_default=True, help="Define the source of BCL folder for soft linking.")
@click.option('-fastq', default="", show_default=True, help="Define the source of FASTQ folder for soft linking.")
@click.option('-multiqc', default="", show_default=True, help="Define the source of the multiqc report for soft linking.")
@click.option('-symprefix', default="/mnt/nextgen", show_default=True, help="Define the prefix of soft link from web server to computational server.")
def export(export_dir, config, user, analysis, bcl, fastq, multiqc, symprefix):
    """Export the raw data, processed data and reports to the export directory by creating soft links without moving around the big files."""
    if os.path.isfile(config):
        gpm = GPM(load_config=config, seqdate=None, application=None, 
                provider=None, piname=None, institute=None, fastq=None, name=None)
        gpm.export(export_dir, symprefix)
        gpm.add_htaccess(export_dir)
        gpm.create_user(export_dir)
    else:
        export_empty_folder(get_gpmconfig("GPM","EXPORT_URL"), export_dir, config, user)
    if analysis:
        # if not os.path.exists(os.path.join(export_dir,"analysis")):
        #     os.makedirs(os.path.join(export_dir,"analysis"))
        os.symlink(analysis, os.path.join(export_dir,"analysis"), target_is_directory=True)
    if os.path.isdir(os.path.join(export_dir,"1_Raw_data")):
        if bcl:
            os.symlink(bcl.rstrip("/"), os.path.join(export_dir,"1_Raw_data", "BCL"), target_is_directory=True)
        if fastq:
            os.symlink(fastq.rstrip("/"), os.path.join(export_dir,"1_Raw_data", "FASTQ"), target_is_directory=True)
    else:
        if bcl:
            os.symlink(bcl.rstrip("/"), os.path.join(export_dir, "BCL"), target_is_directory=True)
        if fastq:
            os.symlink(fastq.rstrip("/"), os.path.join(export_dir, "FASTQ"), target_is_directory=True)
    if multiqc:
        os.symlink(multiqc.rstrip("/"), os.path.join(export_dir, "multiqc"), target_is_directory=True)
    

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
@main.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.argument('targetfolder')
@click.option('--no/--no-behaviour', default=False, show_default=True, help="List the behaviours of the command without actually removing them.")
@click.pass_context
def clean(ctx, targetfolder, no):
    """Clean the temporary files and folders in target folders which shouldn't be archived or backup, such as *fastq.gz, nf-core work folder and result folder."""
    
    def clear_a_folder(target):
        for p in get_gpmconfig("Clean","patterns"):
            target_pattern = os.path.join(target,p)
            # print(target_pattern)
            listfiles = glob.glob(target_pattern)
            if listfiles:
                size_of_files = sum([os.stat(f).st_size for f in listfiles])
                if size_of_files == 4096:
                    size_of_files = sum([get_size(f) for f in listfiles])
                size_of_files = round(size_of_files/(1024*1024*1024),3)
                click.echo("Clean {:7.3f} GB: {}".format(size_of_files, target_pattern))
                # click.echo("Clean "+target_pattern)
                if not no:
                    proc = subprocess.Popen('rm -fr '+target_pattern, shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
    
    clear_a_folder(targetfolder)
    for item in ctx.args:
        clear_a_folder(item)

###################################################################
## archive the folders
###################################################################
@main.command(context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.argument('targetfolder')
@click.option('--backup/--backup-destination', required=True, help="Define the destination folder for archiving the target folders.")
@click.option('-size', default="100M", show_default=True, help="Define the max size of a single file for archiving.")
@click.pass_context
def archive(ctx, targetfolder, size, backup):
    """Archive the folders to the backup destination with filterring the pre-defined file types or folders."""
    def archive_a_folder(targetfolder, size):
        # find large files
        proc = subprocess.Popen('find . -type f -size +'+ size + " " +targetfolder, shell=True,
                                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        def confirm_choice():
            confirm = input("Do you want to archive this folder?\n"+targetfolder+"\n[y]Yes or [n]No: ")
            if confirm != 'y' and confirm != 'n':
                print("\n Invalid Option. Please Enter a Valid Option.")
                return confirm_choice() 
            print (confirm)
            return confirm
        confirm = confirm_choice()

        if confirm=="y":
            proc = subprocess.Popen('rsync --remove-source-files -v --progress -r --max-size='+size+' --checksum '+targetfolder+" "+backup, shell=True,
                                    stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            proc = subprocess.Popen('find -depth -type d -empty -delete '+targetfolder, shell=True,
                                    stdout=subprocess.PIPE,stderr=subprocess.PIPE)    
        else:
            print("Archive process is cancelled.")
   
    # archive_a_folder(targetfolder, size)
    for item in ctx.args:
        archive_a_folder(item, size)

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