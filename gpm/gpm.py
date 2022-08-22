import os
import configparser
from datetime import date, datetime
import getpass
from gpm import version, APPLICATIONS, EXPORT_URL, GROUPNAME
import sys
import shutil
import click
import glob
from .helpers import DisplayablePath, tardir, htpasswd_create_user
from pathlib import Path


class GPM():
    def __init__(self, seqdate, application, provider, piname, institute, fastq, name, load_config=False):
        self.structure = []
        if load_config:
            self.load_config(load_config)
        else:
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
            self.load_structure()
            self.populate_files(command="init")
            self.write_project_config()
        
    def load_structure(self):
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        cfg_path = os.path.join(data_dir, "structure.config")
        with open(cfg_path) as config:
            for line in config:
                if line.startswith("#"): continue
                else:
                    ll = [l.strip() for l in line.split(";")]
                    if len(ll) == 5:
                        self.structure.append(ll)

    def copy_file_replace_vairalbles(self, original, target):
        with open(original, "rb") as f1:
            contents = [l.decode('utf8', 'ignore').rstrip() for l in f1.readlines()]
        modifier = {"FASTQ_DIR": self.fastq,
                    "GPM_TITLE_NAME": self.name,
                    "GPM_PROJECTNAME": self.name.replace("_", " "),
                    "GPM_DIR_BASE": self.base,
                    "GPM_URL_1_Raw_data": os.path.join(EXPORT_URL, self.name, "1_Raw_data"),
                    "GPM_URL_2_Processed_data": os.path.join(EXPORT_URL, self.name, "2_Processed_data"),
                    "GPM_URL_3_Reports": os.path.join(EXPORT_URL, self.name, "3_Reports"),
                    "GPM_URL_TAR": os.path.join(EXPORT_URL, self.name, "compressed_tars")}

        for i,line in enumerate(contents):
            for old, new in modifier.items():
                if old in line:
                    contents[i] = contents[i].replace(old, new)

        with open(target, "w") as f2:
            for line in contents:
                print(line, file=f2)

    def populate_files(self, command):   
        if not os.path.exists(self.base):
            os.makedirs(self.base)
        for s in self.structure:
            if s[2]: # file
                if s[1] == command and (s[0]=="all" or s[0]==self.app):
                    data_dir = os.path.join(os.path.dirname(__file__), "data")
                    original = os.path.join(data_dir, s[2])
                    if not s[4]: # no rename
                        target = os.path.join(self.base, s[3], os.path.basename(s[2]))
                    else:
                        target = os.path.join(self.base, s[3], s[4])
                    if original.endswith('.png'):
                        shutil.copyfile(original, target)
                    else:
                        self.copy_file_replace_vairalbles(original, target)

                
            else: # directory
                target = os.path.join(self.base, s[3])
                if not os.path.exists(target):
                    os.makedirs(target)
            
    def write_project_config(self):
        if not os.path.isfile(self.config_path):
            cfgfile = open(self.config_path, "w")
            Config = configparser.ConfigParser(strict=False)
            Config.add_section("Project")
            Config.set("Project", "Name", self.name)
            Config.set("Project", "Sequencing Date", self.date)
            Config.set("Project", "Principal investigator", self.PI)
            Config.set("Project", "Sample Provider", self.provider)
            Config.set("Project", "Institute", self.institute)
            Config.set("Project", "Application", self.app)
            today = date.today()
            Config.set("Project", "Created Date", today.isoformat())
            now = datetime.now()
            Config.set("Project", "Created Time", now.strftime("%H:%M:%S"))
            Config.set("Project", "GPM Version", version)
            username = getpass.getuser()
            Config.set("Project", "User", username)
            Config.set("Project", "FASTQ Path", self.fastq)
            Config.set("Project", "Base Path", self.base)

            Config.add_section("Log")
            Config.set("Log", now.strftime("%Y-%m-%d %H-%M-%S"), username + " gpm init " + self.base)

            Config.write(cfgfile)
            cfgfile.close()
        else:
            click.echo("***** config.ini file exists already. Please remove it if you want to create a new config.ini.")
            sys.exit()
    
    def update_config(self, action):
        if not os.path.isfile(self.config_path):
            click.echo("***** config.ini file doesn't exist. Please make sure that you have initiated this project with gpm init")
            sys.exit()
        else:
            Config = configparser.ConfigParser(strict=False)
            Config.read(self.config_path)
            now = datetime.now()
            username = getpass.getuser()
            Config.set("Log", now.strftime("%Y-%m-%d %H-%M-%S"), username + " " + action)
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
            # print(str(path))
            click.echo(path.displayable())

    def load_config(self, config_path):
        self.config_path = config_path
        Config = configparser.ConfigParser()
        Config.read(self.config_path)
        self.date = Config["Project"]["Sequencing Date"]
        self.PI = Config["Project"]["Principal investigator"]
        self.name = Config["Project"]["Name"]
        self.provider = Config["Project"]["Sample Provider"]
        self.institute = Config["Project"]["Institute"]
        self.fastq = Config["Project"]["FASTQ Path"]
        self.base = Config["Project"]["Base Path"]
        self.app = Config["Project"]["Application"]
    
    def analysis(self):
        self.load_structure()
        self.populate_files(command="analysis")
        self.update_config("gpm analysis")

    def load_export_config(self):
        convert_list = {"GPM_FASTQ": self.fastq}
        self.export_structure = []
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        cfg_path = os.path.join(data_dir, "export", "export.config")
        with open(cfg_path) as config:
            for line in config:
                if line.startswith("#"): continue
                else:
                    ll = [l.strip() for l in line.split(";")]
                    if len(ll) == 4:
                        if ll[0] == "all" or ll[0] == self.app:
                            for k, v in convert_list.items():
                                if ll[1] == k:
                                    ll[1] = v
                            self.export_structure.append(ll)

    def export(self, export_dir, tar=False):
        def handle_rename(export_dir, entry):
            print(os.path.basename(entry[1]))
            if entry[3]:
                target = os.path.join(export_dir, entry[2], entry[3])
            else:
                target = os.path.join(export_dir, entry[2], os.path.basename(entry[1]))
            return target
        
        self.update_config("gpm export")
        export_dir = os.path.abspath(export_dir)

        # Create the target folder
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            # shutil.chown(export_dir, group=GROUPNAME)
        # Creating soft links of the files
        self.load_export_config()
        for entry in self.export_structure:
            # print(entry)
            if not entry[1]:
                target = os.path.join(export_dir, entry[2])
                if not os.path.exists(target):
                    os.makedirs(target)
            else:
                origin_file = os.path.join(self.base, entry[1])
                # A directory
                if os.path.isdir(origin_file):  
                    target = handle_rename(export_dir, entry)
                    os.symlink(origin_file, target, target_is_directory=True)
                # A file
                elif os.path.isfile(origin_file):  
                    target = handle_rename(export_dir, entry)
                    os.symlink(origin_file, target, target_is_directory=False)
                # A pattern for many files
                else:
                    target_dir = os.path.join(export_dir, entry[2])
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    for matching_file in glob.glob(origin_file):
                        target = os.path.join(target_dir, os.path.basename(matching_file))
                        os.symlink(matching_file, target, target_is_directory=False)
        
    def create_user(self, export_dir):
        export_URL = os.path.join(EXPORT_URL, self.name)
        htpasswd_create_user(export_dir, export_URL, self.provider.lower(), self.app)

    def add_htaccess(self, export_dir):
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        htaccess_path = os.path.join(data_dir, "export", "htaccess")
        self.copy_file_replace_vairalbles(htaccess_path, os.path.join(export_dir, ".htaccess"))
        # shutil.chown(os.path.join(export_dir, ".htaccess"), group=GROUPNAME)

    def generate_index_html(self, export_dir):
        index_path = os.path.join(export_dir, "index.html")
        print(index_path)
        for report_html in glob.glob(export_dir+'/3_Reports/Analysis_Report*.html'):
            print(report_html)
            shutil.copy(report_html, index_path)
    
    def tar_exports(self, export_dir):
        compressed_folder = os.path.join(export_dir, "compressed_tars")
        tardir(os.path.join(export_dir, "1_Raw_data"), os.path.join(compressed_folder, self.name+"_1_Raw_data.tar"))
        tardir(os.path.join(export_dir, "2_Processed_data"), os.path.join(compressed_folder, self.name+"_2_Processed_data.tar"))
        tardir(os.path.join(export_dir, "3_Reports"), os.path.join(compressed_folder, self.name+"_3_Reports.tar"))
        