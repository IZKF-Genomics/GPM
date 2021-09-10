import os
import configparser
from datetime import date, datetime
import getpass
from nextgen import version, APPLICATIONS
import sys
import shutil
import click
from .helpers import DisplayablePath
from pathlib import Path

class Nextgen():
    def __init__(self, seqdate, application, provider, piname, institute, fastq, name):
        self.date = seqdate
        self.PI = piname
        self.name = name
        self.provider = provider
        self.institute = institute
        self.fastq = fastq
        self.base = os.path.join(os.getcwd(), self.name)
        assert application in APPLICATIONS
        self.app = application
        self.config_path = os.path.join(self.base, "config.ini")
        self.structure = []
        self.load_structure()
        self.populate_files()
        self.write_project_config()
        
    def load_structure(self):
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        cfg_path = os.path.join(data_dir, "structure.config")
        with open(cfg_path) as config:
            for line in config:
                if line.startswith("#"): continue
                else:
                    ll = [l.strip(";") for l in line.split()]
                    if len(ll) == 4:
                        self.structure.append(ll)

    def populate_files(self, tag="init"):   
        if not os.path.exists(self.base):
            os.makedirs(self.base)
        for s in self.structure:
            if "." not in s[1]: # directories
                target = os.path.join(self.base, s[0], s[1])
                if not os.path.exists(target):
                    os.makedirs(target)
            else: # files
                if s[2] == tag and (s[3]=="all" or s[3]==self.app):
                    data_dir = os.path.join(os.path.dirname(__file__), "data")
                    original = os.path.join(data_dir, s[1])
                    target = os.path.join(self.base, s[0], s[1])
                    shutil.copyfile(original, target)
            
    def write_project_config(self):
        if not os.path.isfile(self.config_path):
            cfgfile = open(self.config_path, "w")
            Config = configparser.ConfigParser()
            Config.add_section("Project")
            Config.set("Project", "Sequencing Date", self.date)
            Config.set("Project", "Principal investigator", self.PI)
            Config.set("Project", "Sample Provider", self.provider)
            Config.set("Project", "Institute", self.institute)
            Config.set("Project", "Application", self.app)
            today = date.today()
            Config.set("Project", "Created Date", today.isoformat())
            now = datetime.now()
            Config.set("Project", "Created Time", now.strftime("%H:%M:%S"))
            Config.set("Project", "Nextgen Version", version)
            username = getpass.getuser()
            Config.set("Project", "User", username)
            Config.set("Project", "FASTQ Path", self.fastq)
            Config.set("Project", "Analysis Path", self.base)

            Config.add_section("Log")
            Config.set("Log", now.strftime("%Y-%m-%d %H:%M:%S"), username + " created " + self.base)

            Config.write(cfgfile)
            cfgfile.close()
        else:
            click.echo("***** config.ini file exists already. Please remove it if you want to create a new config.ini.")
            sys.exit()
    
    def update_config(self, action):
        if not os.path.isfile(self.config_path):
            click.echo("***** config.ini file doesn't exist. Please make sure that you have initiated this project with nextgen init")
            sys.exit()
        else:
            Config = configparser.ConfigParser()
            Config.read(self.config_path)
            now = datetime.now()
            # username = getpass.getuser()
            Config.set("Log", now.strftime("%Y-%m-%d %H:%M:%S"), action)
            cfgfile = open(self.config_path, "w")
            Config.write(cfgfile)
            cfgfile.close()

    def show_config(self):
        """Show config file in the terminal"""
        click.echo(click.style("Config file:", fg='bright_green'))
        click.echo(self.config_path)
        Config = configparser.ConfigParser()
        Config.read(self.config_path)
        for each_section in Config.sections():
            for (each_key, each_val) in Config.items(each_section):
                click.echo("\t".join([each_key, each_val]))

    def show_tree(self):
        click.echo(click.style("The current status of the project directory:", fg='bright_green'))
        paths = DisplayablePath.make_tree(Path(self.base))
        for path in paths:
            click.echo(path.displayable())
            
    



