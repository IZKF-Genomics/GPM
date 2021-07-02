import os
import ConfigParser
from datetime import date, datetime
import getpass
from nextgen import version
import sys

APPLICATIONS = []


class Nextgen():
    def __init__(self, seq_date, application, PI):
        self.date = seq_date
        self.PI = PI
        self.name = "_".join(seq_date, PI, application)
        self.base = os.path.join(os.getcwd(), self.name)
        assert application in APPLICATIONS
        self.app = application
        self.config_path = os.path.join(self.base, "config.ini")
        self.load_config()
        self.structure = []


    def load_config(self):
        cfg_path = os.path.join(os.path.dirname(__file__), "structure.config")
        with open(cfg_path) as config:
            for line in config:
                if line.startswith("#"): continue
                else:
                    ll = [l.strip(";") for l in line.split()]
                    self.structure.append(ll)
                    
    def write_project_config(self):
        
        if not os.path.isfile(self.config_path):
            cfgfile = open(self.config_path, "w")
            Config = ConfigParser.ConfigParser()
            Config.add_section("Project")
            Config.set("Project", "Sequencing Date", self.date)
            Config.set("Project", "PI", self.PI)
            Config.set("Project", "Application", self.app)
            today = date.today()
            Config.set("Project", "Created Date", today.isoformat())
            now = datetime.now()
            Config.set("Project", "Created Time", now.strftime("%H:%M:%S"))
            Config.set("Project", "Nextgen Version", version)
            username = getpass.getuser()
            Config.set("Project", "User", username)
            Config.set("Project", "Path", self.base)

            Config.add_section("Log")
            Config.set("Log", now.strftime("%Y-%m-%d %H:%M:%S"), username + " created " + self.base)

            Config.write(cfgfile)
            cfgfile.close()
        else:
            print("***** config.ini file exists already. Please remove it \n\
                   ***** if you want to create a new one config.ini.")
            sys.exit()
    
    def update_config(self, action):
        if not os.path.isfile(self.config_path):
            print("***** config.ini file doesn't exist. Please make sure \n\
                   ***** that you have initiated this project with \n\
                   ***** nextgen init")
            sys.exit()
        else:
            Config = ConfigParser.ConfigParser()
            Config.read('self.config_path')
            now = datetime.now()
            # username = getpass.getuser()
            Config.set("Log", now.strftime("%Y-%m-%d %H:%M:%S"), action)
            cfgfile = open(self.config_path, "w")
            Config.write(cfgfile)
            cfgfile.close()


            
            
            
            


