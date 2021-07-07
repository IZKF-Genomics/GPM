import sys
import click
import re
from nextgen.nextgen import Nextgen
from nextgen import version, APPLICATIONS
# from nextgen.nextgen import Nextgen
from nextgen.helpers import DisplayablePath
from pathlib import Path

def show_tree():
    click.echo("The current status of the project directory:")
    paths = DisplayablePath.make_tree(Path(nextgen.base))
    for path in paths:
        click.echo(path.displayable())


@click.group()
@click.version_option(version)
def main():
    """A project management CLI for bioinformatic workflows."""
    pass

@main.command()
def init():
    """Initiate a new project."""
    # click.echo('> Enter the date for sequencing (YYYYMMDD, such as 20210228):')
    # seqdate = input()
    # click.echo('> Choose the application by entering the number:')
    # for i,app in enumerate(APPLICATIONS):
    #     click.echo("\t".join(['\t', str(i+1), app]))
    # app = input()
    # app = APPLICATIONS[int(app)-1]
    # click.echo('> Enter the surname of the PI:')
    # PI = input().capitalize()

    # nextgen = Nextgen(seqdate, app, PI)
    nextgen = Nextgen("20210705", "mRNAseq", "Kuo")
    # print(nextgen.structure)
    show_tree()

if __name__ == '__main__':
    # args = sys.argv
    # if "--help" in args or len(args) == 1:
    #     print("CVE")
    main()