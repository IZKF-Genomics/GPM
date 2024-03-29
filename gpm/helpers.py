from pathlib import Path
import os
import sys
import glob
import shutil
import click
# import tarfile
import subprocess
import random
import string
from configparser import ConfigParser
# import codecs
import json
import configparser
import getpass
from datetime import date, datetime
from gpm import version
from collections import OrderedDict


class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '
    
    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())

        ignore_paths = get_gpmconfig("GPM", "file_tree_ignore")
        new_children = []
        for child in children:
            # print(child)
            tag_ignore = False
            for p in ignore_paths:
                if p in str(child):
                    tag_ignore = True
            if not tag_ignore:
                new_children.append(child)

        count = 1
        for path in new_children:
            is_last = count == len(new_children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))


def fastq_dir_to_samplesheet(
    fastq_dir,
    samplesheet_file,
    strandedness="unstranded",
    read1_extension="_R1_001.fastq.gz",
    read2_extension="_R2_001.fastq.gz",
    single_end=False,
    sanitise_name=False,
    sanitise_name_delimiter="_",
    sanitise_name_index=1,
    sc=False,
    r16s=False
):
    def sanitize_sample(path, extension):
        """Retrieve sample id from filename"""
        sample = os.path.basename(path).replace(extension, "")
        if sanitise_name:
            sample = sanitise_name_delimiter.join(
                os.path.basename(path).split(sanitise_name_delimiter)[
                    :sanitise_name_index
                ]
            )
        return sample

    def get_fastqs(extension):
        """
        Needs to be sorted to ensure R1 and R2 are in the same order
        when merging technical replicates. Glob is not guaranteed to produce
        sorted results.
        See also https://stackoverflow.com/questions/6773584/how-is-pythons-glob-glob-ordered
        """
        return sorted(
            glob.glob(os.path.join(fastq_dir, f"*{extension}"), 
                      recursive=False)
        )

    read_dict = {}

    # Get read 1 files
    for read1_file in get_fastqs(read1_extension):
        sample = sanitize_sample(read1_file, read1_extension)
        if sample not in read_dict:
            read_dict[sample] = {"R1": [], "R2": []}
        read_dict[sample]["R1"].append(read1_file)

    # Get read 2 files
    if not single_end:
        for read2_file in get_fastqs(read2_extension):
            sample = sanitize_sample(read2_file, read2_extension)
            read_dict[sample]["R2"].append(read2_file)

    # Write to file
    if len(read_dict) > 0:
        out_dir = os.path.dirname(samplesheet_file)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        with open(samplesheet_file, "w") as fout:
            if sc:
                header = ["sample", "fastq_1", "fastq_2"]
            elif r16s: 
                header = ["sampleID", "forwardReads", "reverseReads","run"]
            else:
                header = ["sample", "fastq_1", "fastq_2", "strandedness"]
            fout.write(",".join(header) + "\n")
            for sample, reads in sorted(read_dict.items()):
                for idx, read_1 in enumerate(reads["R1"]):
                    read_2 = ""
                    if idx < len(reads["R2"]):
                        read_2 = reads["R2"][idx]
                    if sc:
                        sample_info = ",".join([sample, read_1, read_2])
                    elif r16s:
                        sample_info = ",".join([sample, read_1, read_2],"1")
                    else:
                        sample_info = ",".join([sample, read_1, read_2,
                                                strandedness])
                    fout.write(f"{sample_info}\n")
    else:
        error_str = (
            "\nWARNING: No FastQ files found so samplesheet has not been created!\n\n"
        )
        error_str += "Please check the values provided for the:\n"
        error_str += "  - Path to the directory containing the FastQ files\n"
        error_str += "  - '--read1_extension' parameter\n"
        error_str += "  - '--read2_extension' parameter\n"
        print(error_str)
        sys.exit(1)


def generate_samples(STRANDEDNESS, FASTQ_DIR, SAMPLESHEET_FILE,
                     READ1_EXTENSION, READ2_EXTENSION, SINGLE_END,
                     SANITISE_NAME, SANITISE_NAME_DELIMITER,
                     SANITISE_NAME_INDEX):

    strandedness = "unstranded"
    if STRANDEDNESS in ["unstranded", "forward", "reverse"]:
        strandedness = STRANDEDNESS

    fastq_dir_to_samplesheet(
        fastq_dir=FASTQ_DIR,
        samplesheet_file=SAMPLESHEET_FILE,
        strandedness=strandedness,
        read1_extension=READ1_EXTENSION,
        read2_extension=READ2_EXTENSION,
        single_end=SINGLE_END,
        sanitise_name=SANITISE_NAME,
        sanitise_name_delimiter=SANITISE_NAME_DELIMITER,
        sanitise_name_index=SANITISE_NAME_INDEX,
    )


def generate_samples_scrna(fastq_dir, samplesheet_file):
    """
    Reads must be Must be aligned with: "[Sample Name]_S1_L00[Lane Number]_[Read Type]_001.fastq.gz"
    Besides that, the sample name given in the samplesheet must be the same that is present in the reads name.
    As explained here: https://nf-co.re/scrnaseq/2.1.0/usage#if-using-cellranger
    """
    fastq_dir_to_samplesheet(
        fastq_dir=fastq_dir,
        samplesheet_file=samplesheet_file,
        sanitise_name=True,
        sc=True,
    )

def generate_samples_16s(fastq_dir, samplesheet_file):
    """
    Reads must be Must be aligned with: "[Sample Name]_S1_L00[Lane Number]_[Read Type]_001.fastq.gz". column "run" is not defined yet.
    """
    fastq_dir_to_samplesheet(
        fastq_dir=fastq_dir,
        samplesheet_file=samplesheet_file,
        sanitise_name=True,
        r16s=True
    )

def write_file_run_bcl2fastq(rawfolder, targetfolder):
    data_dir = os.path.join(os.path.dirname(__file__), "data", "demultiplex/bcl2fastq")
    original = os.path.join(data_dir, "run_bcl2fastq.sh")
    target = os.path.join(targetfolder, "run_bcl2fastq.sh")
    with open(original) as f1:
        contents = [le.strip() for le in f1.readlines()]
    
    modifier = {"FLOWCELL_DIR": rawfolder,
                "OUTPUT_DIR": targetfolder}
    for i,line in enumerate(contents):
        for old, new in modifier.items():
            if old in line:
                contents[i] = line.replace(old, new)

    with open(target, "w") as f2:
        for line in contents:
            print(line, file=f2)


def write_file_run_qc(rawfolder, targetfolder):
    data_dir = os.path.join(os.path.dirname(__file__), "data", "demultiplex/bcl2fastq")
    original = os.path.join(data_dir, "run_qc.sh")
    target = os.path.join(targetfolder, "run_qc.sh")
    raw_folder_extended = os.path.join(rawfolder, "Alignment_1" , "*" , "Fastq")
    with open(original) as f1:
        contents = [le.strip() for le in f1.readlines()]

    modifier = {"FASTQ_DIR": raw_folder_extended,
                "OUTPUT_DIR": targetfolder}
    for i, line in enumerate(contents):
        for old, new in modifier.items():
            if old in line:
                contents[i] = line.replace(old, new)

    with open(target, "w") as f2:
        for line in contents:
            print(line, file=f2)


def write_file_run_cellranger_mkfastq(rawfolder, targetfolder):
    data_dir = os.path.join(os.path.dirname(__file__), "data", "demultiplex/cellranger")
    original = os.path.join(data_dir, "run_cellranger_mkfastq.sh")
    target = os.path.join(targetfolder, "run_cellranger_mkfastq.sh")
    with open(original) as f1:
        contents = [le.strip() for le in f1.readlines()]
    
    modifier = {"FLOWCELL_DIR": rawfolder,
                "OUTPUT_DIR": targetfolder}
    for i, line in enumerate(contents):
        for old, new in modifier.items():
            if old in line:
                contents[i] = line.replace(old, new)

    with open(target, "w") as f2:
        for line in contents:
            print(line, file=f2)


def write_file_run_cellranger_merge_lanes(rawfolder, targetfolder):
    data_dir = os.path.join(os.path.dirname(__file__), "data", "demultiplex/cellranger")
    original = os.path.join(data_dir, "run_merge_lanes.sh")
    target = os.path.join(targetfolder, "run_merge_lanes.sh")
    with open(original) as f1:
        contents = [le.strip() for le in f1.readlines()]
    flowcell_id = targetfolder.split("/")[-1][-9:]
    FASTQ_path = os.path.join(targetfolder, "mkfastq", "outs",
                              "fastq_path", flowcell_id)

    modifier = {"CELLRANGER_FASTQ_PATH": FASTQ_path,
                "OUTPUT_DIR": os.path.join(targetfolder, "merged_fastq")}
    for i, line in enumerate(contents):
        for old, new in modifier.items():
            if old in line:
                contents[i] = line.replace(old, new)

    with open(target, "w") as f2:
        for line in contents:
            print(line, file=f2)

def write_file_run_idemux(rawfolder, targetfolder):
    data_dir = os.path.join(os.path.dirname(__file__), "data", "demultiplex/bcl2fastq")
    original = os.path.join(data_dir, "run_idemux.sh")
    target = os.path.join(targetfolder, "run_idemux.sh")
    fastq_folder_full_path = os.path.join("/data/fastq", targetfolder)
    with open(original) as f1:
        contents = [le.strip() for le in f1.readlines()]
    
    modifier = {"FLOWCELL_DIR": rawfolder,
                "OUTPUT_DIR": targetfolder,
                "FASTQ_DIR": fastq_folder_full_path}
    
    for i,line in enumerate(contents):
        for old, new in modifier.items():
            if old in line:
                contents[i] = line.replace(old, new)

    with open(target, "w") as f2:
        for line in contents:
            print(line, file=f2)

def copyfromdata(filename, targetdir):
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    original = os.path.join(data_dir, filename)
    target = os.path.join(targetdir, filename.split("/")[-1])
    shutil.copyfile(original, target)


def show_tree(base):
    click.echo(click.style("The current status of the project directory:",
                           fg='bright_green'))
    paths = DisplayablePath.make_tree(Path(base))
    for path in paths:
        click.echo(path.displayable())


def move_igv(igv_session):
    # define path
    igv_path = os.path.abspath(igv_session)
    # copy the file
    result_dir = os.path.abspath(os.path.join(igv_path, "../../.."))
    target = os.path.join(result_dir, "igv_session.xml")
    shutil.copyfile(igv_path, target)
    # remove relative path
    fin = open(target, "rt")
    data = fin.read()
    data = data.replace('../../', './')
    fin.close()
    fin = open(target, "wt")
    fin.write(data)
    fin.close()


def tardir(path, tar_name):
    # subprocess.run(["SOURCE="+'\"'+path+'\"'], shell=True)
    # subprocess.run(['SOURCE_SIZE=$(du -sk \"${SOURCE}\" | cut -f1)'], shell=True)
    # subprocess.run(['tar -hcf - \"${SOURCE}\" | pv -p -s \"${SOURCE_SIZE}k\" > '+tar_name], shell=True)
    # archive and compress
    # tar -cf - "${SOURCE}" | pv -p -s "${SOURCE_SIZE}k" | xz -6 --threads=6 -c -

    cmd = " ".join(["tar", "-hcf", tar_name, "--absolute-names", path])
    returned_value = subprocess.call(cmd, shell=True)
    cmd = " ".join(["md5sum", tar_name, ">", tar_name+".md5"])
    returned_value = subprocess.call(cmd, shell=True)


def tar_exports(export_dir, nobehaviour):
    if export_dir == ".":
        export_dir = os.getcwd()
    export_dir = export_dir.rstrip("/")
    name = os.path.basename(export_dir)
    compressed_folder = os.path.join(export_dir, "compressed_tars")
    if not os.path.exists(compressed_folder):
        click.echo(click.style("Create the folder:", fg='bright_green'))
        click.echo(compressed_folder)
        if not nobehaviour:
            os.makedirs(compressed_folder)

    for filename in os.listdir(export_dir):
        pathfile = os.path.join(export_dir, filename)
        tarfile = os.path.join(compressed_folder, name+"_" + filename + ".tar")
        if os.path.islink(pathfile):
            pathfile = os.readlink(pathfile)
            base_dirs = ["/mnt/nextgen", "/mnt/nextgen2", "/mnt/nextgen3"]
            for base_dir in base_dirs:
                if pathfile.startswith(base_dir):
                    # Getting the relative path of the directory
                    rel_path = os.path.relpath(pathfile, base_dir)
                    pathfile = os.path.join("/", rel_path)
        if os.path.isdir(pathfile) and filename != "compressed_tars":
            click.echo(click.style("Tar the folder:", fg='bright_green'))
            click.echo(pathfile + click.style(" => ",
                                              fg='bright_green') + tarfile)
            if not nobehaviour:
                tardir(pathfile, tarfile)

   
def htpasswd_create_user(target_dir, url, username, app, raw_export=False):
    """Create the new user in the target directory with password"""
    export_base_path = Path(target_dir).parent.absolute()
    if os.path.exists(os.path.join(export_base_path, ".htpasswd")):
        shutil.copy(os.path.join(export_base_path, ".htpasswd"), 
                    os.path.join(target_dir, ".htpasswd"))
        password = generate_password()
        cmd = " ".join(["htpasswd", "-b",
                        os.path.join(target_dir, ".htpasswd"), 
                        username, password])
        # returned_value = subprocess.call(cmd, shell=True)
        # print(cmd)
        subprocess.run(cmd, shell=True)
        click.echo()
        click.echo(click.style("Create new user for export directory:",
                               fg='bright_green'))
        click.echo("Directory:\t" + target_dir)
        if app and not raw_export:
            if app in ["RNAseq", "tRNAseq", "mRNAseq", "3mRNAseq"]:
                app = "RNAseq"
            click.echo("".join(["URL:\t", url,
                                "/3_Reports/analysis/Analysis_Report_",
                                app, ".html"]))
        else:
            click.echo("URL:\t" + url)
        click.echo("user:\t" + username)
        click.echo("password:\t" + password)
    else:
        click.echo("Skip setting htpasswd")


def create_user(export_dir, export_URL, username):
    htpasswd_create_user(export_dir, export_URL, username, None)


def generate_password():
    source = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(source) for i in range(12)))
    return result_str


def export_empty_folder(export_URL, export_dir, config, user):
    export_dir = os.path.abspath(export_dir)
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    # Add htaccess
    # data_dir = os.path.join(os.path.dirname(__file__), "data")
    htaccess_path = get_config("htaccess")
    with open(htaccess_path) as f1:
        contents = [le.rstrip() for le in f1.readlines()]
    for i, line in enumerate(contents):
        if "GPM_TITLE_NAME" in line:
            contents[i] = line.replace("GPM_TITLE_NAME",
                                       os.path.basename(export_dir))

    with open(os.path.join(export_dir, ".htaccess"), "w") as f2:
        for line in contents:
            print(line, file=f2)
    # Create user
    htpasswd_create_user(export_dir,
                         os.path.join(export_URL,
                                      os.path.basename(export_dir)), 
                         user.lower(), None)


def get_gpmdata_path():
    return os.path.expanduser(os.getenv("GPMDATA",
                                        os.path.join(os.getenv("HOME"),
                                                     "gpmdata")))


def get_gpmconfig(section, item):
    # Return the content in the config file. The user defined config has
    # higher priority than the default config.
    # config.read_file(codecs.open(gpmconfig, "r", "utf8"))
    gpmconfig = os.path.join(get_gpmdata_path(), "gpm.config.user")
    if not os.path.exists(gpmconfig):
        gpmconfig = os.path.join(get_gpmdata_path(), "gpm.config")

    config = ConfigParser()
    config.read(gpmconfig)
    # config.read_file(codecs.open(gpmconfig, "r", "utf8"))
    # print(config.sections())
    # print(config[section][item])
    # config.read_file(codecs.open(gpmconfig, "r", "utf8"))
    res = config.get(section, item)
    if res[0] == "[":
        res = json.loads(res)
    return res


def get_config(config_name):
    cfg_path = os.path.join(get_gpmdata_path(), config_name+".user")
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(get_gpmdata_path(), config_name)
    return cfg_path


def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def generate_config_file(fastq, output, raw):
    base = os.path.join(os.getcwd(), output)
    config_path = os.path.join(base, "config.ini")

    if not os.path.isfile(config_path):
        cfgfile = open(config_path, "w")
        Config = configparser.ConfigParser(strict=False)
        Config.add_section("Project")
        today = date.today()
        Config.set("Project", "Created Date", today.isoformat())
        now = datetime.now()
        Config.set("Project", "Created Time", now.strftime("%H:%M:%S"))
        Config.set("Project", "GPM Version", version)
        username = getpass.getuser()
        Config.set("Project", "User", username)
        Config.set("Project", "FASTQ Path", fastq)
        Config.set("Project", "BCL Path", raw)
        Config.set("Project", "Base Path", base)

        Config.add_section("Log")
        Config.set("Log", now.strftime("%Y-%m-%d %H-%M-%S"),
                   username + " gpm demultiplex " + base)

        Config.write(cfgfile)
        cfgfile.close()
    else:
        click.echo("***** config.ini file exists already. Please remove it" 
                   "if you want to create a new config.ini.")
        sys.exit()


def update_config_with_name(name, Config):
    """Adding to the config file the details about the project 
    (required for export)"""
    split_name = name.split("_")
    seqdate = split_name[0]
    # seqdate
    try:
        datetime.strptime(seqdate, "%y%m%d")
    except ValueError:
        click.echo("""This is the incorrect date string format. 
                   It should be YYMMDD""")
        sys.exit()

    # app
    application = split_name[4]
    if application not in get_gpmconfig("GPM", "APPLICATIONS"):
        click.echo("Please type exactly the app name in the list: "+" ".join(get_gpmconfig("GPM", "APPLICATIONS")))
        sys.exit()
    # surnames
    provider = split_name[1].capitalize()
    piname = split_name[2].capitalize()
    institute = split_name[3]
    Config.set("Project", "Name", name)
    Config.set("Project", "Sequencing Date", seqdate)
    Config.set("Project", "Principal investigator", piname)
    Config.set("Project", "Sample Provider", provider)
    Config.set("Project", "Institute", institute)
    Config.set("Project", "Application", application)

    return Config