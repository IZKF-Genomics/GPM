import sys
import click
import re
import os
import fnmatch
from .nextgen import Nextgen
from . import version, APPLICATIONS
from .helpers import DisplayablePath
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
###################################################################
@main.command()
@click.option('--base', default=".", help=helps["base"])
@click.option('--fastq', help=helps["fastq"])
def samplesheet(base, fastq):
    """Generate the sample sheet for FASTQ files."""
    PE = False
    if os.path.isfile(os.path.join(base, 'config.ini')):
        path_samplesheet = os.path.join(base, "nfcore", "samplesheet.csv")
    else:
        click.echo("config.ini is not found in the base directory. You either defined the wrong base directory or didn't do nextgen init command yet.")
        sys.exit()
    
    fastqs_filenames = []
    for file in os.listdir(fastq):
        if fnmatch.fnmatch(file, '*.fastq.gz') or fnmatch.fnmatch(file, '*.fq.gz'):
            fastqs_filenames.append(file)
    fastqs_filenames.sort()
    
    # Process names and pairs
    tags_pe = [r"*read[1-2]*", r"*R[1-2]*"]
    for tag in tags_pe:
        # print(fnmatch.fnmatch(fastqs_filenames[0], tag))
        if fnmatch.fnmatch(fastqs_filenames[0], tag):
            PE =  True

    if PE:
        PE_dict = {}
        for file in fastqs_filenames:
            for tag in tags_pe:
                if fnmatch.fnmatch(fastqs_filenames[0], tag):
                    l = file.split(".")
                    ll = [x for x in l if x not in ["fastq", "fq", "gz"]]
                    r = re.compile("."+tag)
                    t = list(filter(r.match, ll))[0]
                    # ll.remove(t)
                    # ll = [x for x in ll if x != t]
                    # print(t)
                    # print(ll)

                    if ll[0] not in PE_dict.keys():
                        PE_dict[ll[0]] = {}
                    PE_dict[ll[0]][t] = os.path.join(fastq, file)
        PE_dict = collections.OrderedDict(sorted(PE_dict.items()))
        for lab in PE_dict.keys():
            PE_dict[lab] = collections.OrderedDict(sorted(PE_dict[lab].items()))
        with open(path_samplesheet, "w") as f:
            print("sample,fastq_1,fastq_2,strandedness", file=f)
            for k, v in PE_dict.items():
                l = list(v.values())
                print(",".join([k, l[0], l[1], "unstranded"]), file=f)
    else:
        with open(path_samplesheet, "w") as f:
            print("sample,fastq_1,fastq_2,strandedness", file=f)
            for file in fastqs_filenames:
                l = file.split(".")
                ll = [x for x in l if x not in ["fastq", "fq", "gz"]]
                print(",".join([".".join(ll), 
                                os.path.join(fastq, file), 
                                "", "unstranded"]), file=f)
            



if __name__ == '__main__':
    # args = sys.argv
    # if "--help" in args or len(args) == 1:
    #     print("CVE")
    main()