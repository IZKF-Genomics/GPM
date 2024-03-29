import os
import configparser
from datetime import date, datetime
import getpass
from gpm import version
import sys
import shutil
import click
import glob
import subprocess
from collections import OrderedDict
from .helpers import (
    DisplayablePath,
    tardir,
    htpasswd_create_user,
    get_gpmconfig,
    get_gpmdata_path,
    get_config,
    tar_exports)

import pandas as pd
from pathlib import Path


class GPM():
    def __init__(self, seqdate, application, provider,
                 piname, institute, fastq, name, load_config=False):
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
            assert application in get_gpmconfig("GPM", "APPLICATIONS")
            self.app = application
            self.config_path = os.path.join(self.base, "config.ini")
            self.load_structure()
            self.populate_files(command="init")
            self.write_project_config()
        
    def load_structure(self):
        cfg_path = get_config("files.config")
        with open(cfg_path) as config:
            for line in config:
                if line.startswith("#"):
                    continue
                else:
                    if "GPMDATA" in line:
                        line = line.replace("GPMDATA", get_gpmdata_path())
                    ll = [element.strip() for element in line.split(";")]
                    if len(ll) == 5:
                        self.structure.append(ll)

    def copy_file_replace_vairalbles(self, original, target):
        with open(original, "rb") as f1:
            contents = [le.decode('utf8', 'ignore').rstrip() 
                        for le in f1.readlines()]
        authors = get_gpmconfig("Rmd", "authors")
        # authors = get_gpmconfig("Rmd", "authors").strip("[]")
        # authors = authors.split(',\n')
        GPM_URL_1 = os.path.join(get_gpmconfig("GPM", "EXPORT_URL"),
                                 self.name, "1_Raw_data")
        GPM_URL_2 = os.path.join(get_gpmconfig("GPM", "EXPORT_URL"),
                                 self.name, "2_Processed_data")
        GPM_URL_3 = os.path.join(get_gpmconfig("GPM", "EXPORT_URL"),
                                 self.name, "3_Reports")
        GPM_URL_TAR = os.path.join(get_gpmconfig("GPM", "EXPORT_URL"),
                                   self.name, "compressed_tars")
        modifier = {"FASTQ_DIR": self.fastq,
                    "GPM_TITLE_NAME": self.name,
                    "GPM_PROJECTNAME": self.name.replace("_", " "),
                    "GPM_DIR_BASE": self.base,
                    "GPM_URL_1_Raw_data": GPM_URL_1,
                    "GPM_URL_2_Processed_data": GPM_URL_2,
                    "GPM_URL_3_Reports": GPM_URL_3,
                    "GPM_URL_TAR": GPM_URL_TAR,
                    "GPM_AUTHORS": "\n".join('  - ' + ppl for ppl in authors)
                    }

        for i, line in enumerate(contents):
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
            if s[2]:  # file
                if s[1] == command and (s[0] == "all" or s[0] == self.app):
                    data_dir = os.path.join(os.path.dirname(__file__), "data")
                    original = os.path.join(data_dir, s[2])
                    if not s[4]:  # no rename
                        target = os.path.join(self.base,
                                              s[3], os.path.basename(s[2]))
                    else:
                        target = os.path.join(self.base, s[3], s[4])
                    if original.endswith('.png'):
                        shutil.copyfile(original, target)
                    else:
                        self.copy_file_replace_vairalbles(original, target)

            else:  # directory
                if s[1] == command and (s[0] == "all" or s[0] == self.app): 
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
            Config.set("Log", now.strftime("%Y-%m-%d %H-%M-%S"),
                       username + " gpm init " + self.base)

            Config.write(cfgfile)
            cfgfile.close()
        else:
            click.echo("***** config.ini file exists already. Please remove"
                       "it if you want to create a new config.ini.")
            sys.exit()
    
    def update_config(self, action):
        if not os.path.isfile(self.config_path):
            click.echo("***** config.ini file doesn't exist. Please make"
                       "sure that you have initiated this project with"
                       "gpm init")
            sys.exit()
        else:
            Config = configparser.ConfigParser(strict=False)
            Config.read(self.config_path)
            now = datetime.now()
            username = getpass.getuser()
            Config.set("Log", now.strftime("%Y-%m-%d %H-%M-%S"),
                       username + " " + action)
            cfgfile = open(self.config_path, "w")
            Config.write(cfgfile)
            cfgfile.close()

    def add_bcl_to_config(self):
        """Adding the bcl path to the project's config file from the fastq
        config file"""
        # Getting the path from the fastq config file
        current_dir = self.fastq
        while True:
            demultiplexing_config_path = os.path.join(current_dir, "config.ini")
            if os.path.isfile(demultiplexing_config_path):
                break
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                # Reached the root directory without finding the config file
                click.echo("***** config.ini file doesn't exist in the fastq "
                           "folder or its parent directories. GPM is unable to"
                           "add bcl path to the config file")
                sys.exit()
            current_dir = parent_dir

        demultiplexing_config_path = os.path.join(self.fastq, "config.ini")
        if not os.path.isfile(demultiplexing_config_path):
            click.echo("***** config.ini file doesn't exist in the *fastq "
                       "folder*. unable to add bcl path to the config file")
            sys.exit()
        else:
            Config_demultiplexing = configparser.ConfigParser()
            Config_demultiplexing.read(demultiplexing_config_path)
            click.echo("line 151: demultiplexing_config_path: " +
                       demultiplexing_config_path)
            bcl_path = Config_demultiplexing["Project"]["BCL Path"]

        # Update the bcl path in the project's config file  
        if not os.path.isfile(self.config_path):
            click.echo("""***** config.ini file doesn't exist in the *project 
                       folder*. unable to add bcl path to the config file""")
            sys.exit()
        else:
            Config = configparser.ConfigParser()
            Config.read(self.config_path)
            Config.set("Project", "BCL Path", bcl_path)
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
        click.echo(click.style("The current status of the project directory:",
                               fg='bright_green'))
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
        self.generate_analysis_samplesheet()
        self.update_config("gpm analysis")
        
    def generate_analysis_samplesheet(self):
        cwd = os.getcwd()
        nfcore_folder_path = os.path.join(cwd, 'nfcore')
        # read nfcore samplesheet
        try:
            nfcore_samplesheet_df = pd.read_csv(os.path.join(nfcore_folder_path,'samplesheet.csv'))
            
            # Create analysis sample sheet
            try:
                analysis_samplesheet_df = nfcore_samplesheet_df.drop('strandedness',
                                                                    axis=1)
            except:
                analysis_samplesheet_df = nfcore_samplesheet_df
            partial_names = analysis_samplesheet_df['sample'].str.split('_', expand=True)
            column_names = [f"column_{i+1}" for i in range(partial_names.shape[1])]
            analysis_samplesheet_df[column_names] = partial_names

            analysis_folder_path = os.path.join(cwd, 'analysis')
            output_file_path = os.path.join(os.path.join(analysis_folder_path,"DGEA",'samplesheet.csv'))

            with open(output_file_path, "w") as file:
                analysis_samplesheet_df.to_csv(file, index=False)
        except:
            click.echo("No sample sheet is available.")

    def load_export_config(self):
        convert_list = {"GPM_FASTQ": self.fastq}
        self.export_structure = []
        
        cfg_path = get_config("export.config")
        with open(cfg_path) as config:
            for line in config:
                if line.startswith("#"):
                    continue
                else:
                    ll = [le.strip() for le in line.split(";")]
                    if len(ll) == 4:
                        if ll[0] == "all" or ll[0] == self.app:
                            for k, v in convert_list.items():
                                if ll[1] == k:
                                    ll[1] = v
                            self.export_structure.append(ll)

    def export_raw(self, export_dir, symprefix, bcl, fastq,
                   multiqc="", tar=False):
        self.update_config("gpm export_raw")
        export_dir = os.path.abspath(export_dir)
        # Create the target folder
        os.makedirs(export_dir)
        # For BCL files
        origin_file = bcl
        bcl_path = os.path.join(export_dir, 'BCL')
        os.symlink(symprefix+origin_file, bcl_path, target_is_directory=True)
        # For FASTQ files
        origin_file = fastq
        fastq_path = os.path.join(export_dir, 'FASTQ')
        os.symlink(symprefix+origin_file, fastq_path, target_is_directory=True)

        self.add_htaccess(export_dir)
        self.create_user(export_dir, raw_export=True)
        # print multiqc report link
        export_URL = os.path.join(get_gpmconfig("GPM","EXPORT_URL"), self.name)
        multiqc_path = glob.glob("**/multiqc_report.html", recursive=True)[0]
        multiqc_exported_path = os.path.join( export_URL, "FASTQ", multiqc_path)
        click.echo("MultiQC report:\t" + multiqc_exported_path)

        # Tar the export:
        if tar:
            tar_exports(export_dir, False)
        self.generate_demultiplexing_report()
        # Link the new generated report into the export folder:
        demultiplexing_report_path = os.path.join(export_dir, 'Demultiplexing_Report.html')
        origin_file = os.path.join(os.getcwd(), 'Demultiplexing_Report.html')
        os.symlink(symprefix+origin_file, demultiplexing_report_path, target_is_directory=False)

    def generate_demultiplexing_report(self):
        """
        Generate demultiplexing report by rendering a R markdown file, which is generated 
        specifically for this demultiplexing-project.
        """
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        gpm_logo_image_path = os.path.join(data_dir, 'analysis/RWTH_IZKF_GF_Logo_rgb.png')
        references = os.path.join(data_dir, 'analysis/references.bib')
        export_URL = str(os.path.join(get_gpmconfig("GPM", "EXPORT_URL"), self.name))
        bcl_path = os.path.join(export_URL, "BCL")
        fastq_path = os.path.join(export_URL, "FASTQ")
        tar_export_path = os.path.join(export_URL, "compressed_tars")
        multiqc_export_path = os.path.join(export_URL, "FASTQ/multiqc/multiqc_report.html")
        # shutil.copyfile(original, gpm_logo_image)

        demultiplexing_report_path  = os.path.join(data_dir, 'demultiplex/bcl2fastq/demultiplexing_report.Rmd')
        with open(demultiplexing_report_path, "rb") as f1:
            demultiplexing_report_template = [le.decode('utf8', 'ignore').rstrip() 
                        for le in f1.readlines()]
        
        seq_type = self.name.split("_")[-1]
        if seq_type.startswith("sc"):
            method_description = "FASTQ files were generated using cellranger mkfastq (10x Genomics)."
        else:
            method_description = "FASTQ files were generated using bcl2fastq (Illumina)."

        modifier = { "<TITLE>": self.name,
                    "<REFERENCES>": references,
                    "<EXPORT_DIRECTORY>": export_URL,
                    "<TAR_DIRECTORY>": tar_export_path,
                    "<MULTIQC_PATH>": multiqc_export_path,
                    "<BCL_PATH>": bcl_path,
                    "<FASTQ_PATH>":fastq_path,
                    "<IZKF_LOGO>": gpm_logo_image_path,
                    "<METHOD_DESCRIPTION>": method_description
                    }
        
        for i, line in enumerate(demultiplexing_report_template):
            for old, new in modifier.items():
                if old in line:
                    demultiplexing_report_template[i] = demultiplexing_report_template[i].replace(old, new)

        # Create demultiplexing_report.Rmd inside the working folder
        with open(os.path.join(os.getcwd(),'Demultiplexing_Report.Rmd') , "w") as f2:
            for line in demultiplexing_report_template:
                print(line, file=f2)

        commands = '/opt/miniconda3/envs/rstudio/bin/Rscript -e "rmarkdown::render(\'Demultiplexing_Report.Rmd\', output_format = \'html_document\', output_file =\'Demultiplexing_Report.html\')"'

        # Run the Bash commands
        process = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for the process to finish and get the output and error (if any)
        output, error = process.communicate()

        # Print the output
        print("Output:")
        print(output.decode())

        # Print the error
        print("Error:")
        print(error.decode())
        
    
    
    def export(self, export_dir, symprefix, tar=False):
        def handle_rename(export_dir, entry):
            # print(os.path.basename(entry[1]))
            if entry[3]:
                target = os.path.join(export_dir, entry[2], entry[3])
            else:
                target = os.path.join(export_dir, entry[2],
                                      os.path.basename(entry[1]))
            return target

        self.update_config("gpm export")
        export_dir = os.path.abspath(export_dir)
        # symlink_web2comp = get_gpmconfig("GPM", "SYMLINK_From_Web2Comp")

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
                # print(symprefix)
                # print(origin_file)
                # A directory
                if os.path.isdir(origin_file):  
                    target = handle_rename(export_dir, entry)
                    # print(target)
                    os.symlink(symprefix+origin_file, target,
                               target_is_directory=True)
                # A file
                elif os.path.isfile(origin_file):  
                    target = handle_rename(export_dir, entry)
                    os.symlink(symprefix+origin_file, target,
                               target_is_directory=False)
                # A pattern for many files
                else:
                    target_dir = os.path.join(export_dir, entry[2])
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir)
                    for matching_file in glob.glob(origin_file):
                        target = os.path.join(target_dir,
                                              os.path.basename(matching_file))
                        os.symlink(symprefix+matching_file, target,
                                   target_is_directory=False)
        
    def create_user(self, export_dir, raw_export=False):
        export_URL = os.path.join(get_gpmconfig("GPM", "EXPORT_URL"),
                                  self.name)
        htpasswd_create_user(export_dir, export_URL, self.provider.lower(),
                             self.app, raw_export)

    def add_htaccess(self, export_dir):
        # data_dir = os.path.join(os.path.dirname(__file__), "data")
        htaccess_path = get_config("htaccess")
        self.copy_file_replace_vairalbles(htaccess_path,
                                          os.path.join(export_dir,
                                                       ".htaccess"))
        # shutil.chown(os.path.join(export_dir, ".htaccess"), group=GROUPNAME)

    def tar_exports(self, export_dir):
        compressed_folder = os.path.join(export_dir, "compressed_tars")
        tardir(os.path.join(export_dir, "1_Raw_data"),
               os.path.join(compressed_folder,
                            self.name+"_1_Raw_data.tar"))
        tardir(os.path.join(export_dir, "2_Processed_data"),
               os.path.join(compressed_folder,
                            self.name+"_2_Processed_data.tar"))
        tardir(os.path.join(export_dir, "3_Reports"),
               os.path.join(compressed_folder,
                            self.name+"_3_Reports.tar"))
    
    def load_analysis_config(self):
        """Load the analysis config file from GPM into a dictionary."""
        file_analysis_config = get_config(config_name="analysis.config")
        self.analysis_dict = OrderedDict()
        with open(file_analysis_config) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                elif len(line.split(",")) == 3:
                    l = [x.strip() for x in line.split(",")]
                    if l[0] not in self.analysis_dict:
                        self.analysis_dict[l[0]] = OrderedDict()
                    if l[1] not in self.analysis_dict[l[0]]:
                        self.analysis_dict[l[0]][l[1]] = []
                    self.analysis_dict[l[0]][l[1]].append(l[2])

    def analysis_show_templates(self):
        for group in self.analysis_dict.keys():
            click.echo(click.style(group, fg='bright_green'))
            for label in self.analysis_dict[group].keys():
                click.echo("  <<< " + label + " >>>")
                for file in self.analysis_dict[group][label]:
                    click.echo("    " + file.split("/")[2])
            click.echo("")

    def analysis_add(self, target_label):
        dir_analysis = os.path.join(os.path.dirname(__file__), "data")
        # dir_analysis = os.path.join(data_dir, "analysis")
        for group in self.analysis_dict.keys():
            for label in self.analysis_dict[group].keys():
                if label == target_label:
                    group_dir = os.path.join(self.base, "analysis", group)
                    if not os.path.exists(group_dir):
                        os.makedirs(group_dir)
                    for template in self.analysis_dict[group][label]:
                        click.echo("  "+template)
                        self.copy_file_replace_vairalbles(os.path.join(dir_analysis, template),
                                                          os.path.join(self.base, template))