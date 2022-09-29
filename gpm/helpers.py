from pathlib import Path
import os
import sys
import glob
import shutil
import click
import tarfile
import subprocess
import random
import string
from configparser import ConfigParser
import codecs

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

        ignore_paths = ["nfcore/results/", "nfcore/work/", "nfcore/.nextflow/"]
        new_children = []
        for child in children:
            # print(child)
            tag_ignore = False
            for p in ignore_paths:
                if p in str(child):
                    tag_ignore = True
            if not tag_ignore: new_children.append(child)

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

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

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
            glob.glob(os.path.join(fastq_dir, f"*{extension}"), recursive=False)
        )

    read_dict = {}

    ## Get read 1 files
    for read1_file in get_fastqs(read1_extension):
        sample = sanitize_sample(read1_file, read1_extension)
        if sample not in read_dict:
            read_dict[sample] = {"R1": [], "R2": []}
        read_dict[sample]["R1"].append(read1_file)

    ## Get read 2 files
    if not single_end:
        for read2_file in get_fastqs(read2_extension):
            sample = sanitize_sample(read2_file, read2_extension)
            read_dict[sample]["R2"].append(read2_file)

    ## Write to file
    if len(read_dict) > 0:
        out_dir = os.path.dirname(samplesheet_file)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir)

        with open(samplesheet_file, "w") as fout:
            header = ["sample", "fastq_1", "fastq_2", "strandedness"]
            fout.write(",".join(header) + "\n")
            for sample, reads in sorted(read_dict.items()):
                for idx, read_1 in enumerate(reads["R1"]):
                    read_2 = ""
                    if idx < len(reads["R2"]):
                        read_2 = reads["R2"][idx]
                    sample_info = ",".join([sample, read_1, read_2, strandedness])
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
            SANITISE_NAME, SANITISE_NAME_DELIMITER, SANITISE_NAME_INDEX):

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

def write_file_run_bcl2fastq(rawfolder, targetfolder):
    data_dir = os.path.join(os.path.dirname(__file__), "data", "bcl2fastq")
    original = os.path.join(data_dir, "run_bcl2fastq.sh")
    target = os.path.join(targetfolder, "run_bcl2fastq.sh")
    with open(original) as f1:
        contents = [l.strip() for l in f1.readlines()]
    
    modifier = {"FLOWCELL_DIR": rawfolder,
                "OUTPUT_DIR": targetfolder}
    for i,line in enumerate(contents):
        for old, new in modifier.items():
            if old in line:
                contents[i] = line.replace(old, new)

    with open(target, "w") as f2:
        for line in contents:
            print(line, file=f2)

def write_file_run_cellranger_mkfastq(rawfolder, targetfolder):
    data_dir = os.path.join(os.path.dirname(__file__), "data", "bcl2fastq")
    original = os.path.join(data_dir, "run_cellranger.sh")
    target = os.path.join(targetfolder, "run_cellranger.sh")
    with open(original) as f1:
        contents = [l.strip() for l in f1.readlines()]
    
    modifier = {"FLOWCELL_DIR": rawfolder,
                "OUTPUT_DIR": targetfolder}
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
    click.echo(click.style("The current status of the project directory:", fg='bright_green'))
    paths = DisplayablePath.make_tree(Path(base))
    for path in paths:
        click.echo(path.displayable())

def move_igv(igv_session):
    # define path
    igv_path = os.path.abspath(igv_session)
    # copy the file
    result_dir = os.path.abspath(os.path.join(igv_path ,"../../.."))
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

    cmd = " ".join(["tar","-hcf",tar_name,"--absolute-names", path])
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
        tarfile = os.path.join(compressed_folder, name+"_" +filename+".tar")
        if os.path.isdir(pathfile) and filename != "compressed_tars":
            click.echo(click.style("Tar the folder:", fg='bright_green'))
            click.echo(pathfile +click.style(" => ", fg='bright_green')+ tarfile)
            if not nobehaviour:
                tardir(pathfile, tarfile)

    # tardir(os.path.join(export_dir, "1_Raw_data"), os.path.join(compressed_folder, name+"_1_Raw_data.tar"))
    # tardir(os.path.join(export_dir, "2_Processed_data"), os.path.join(compressed_folder, name+"_2_Processed_data.tar"))
    # tardir(os.path.join(export_dir, "3_Reports"), os.path.join(compressed_folder, name+"_3_Reports.tar"))
        
def htpasswd_create_user(target_dir, url, username, app):
    """Create the new user in the target directory with password"""
    export_base_path = Path(target_dir).parent.absolute()
    if os.path.exists(os.path.join(export_base_path, ".htpasswd")):
        shutil.copy(os.path.join(export_base_path, ".htpasswd"), 
                    os.path.join(target_dir, ".htpasswd"))
        password = generate_password()
        cmd = " ".join(["htpasswd", "-b", os.path.join(target_dir,".htpasswd"), username, password])
        # returned_value = subprocess.call(cmd, shell=True)
        # print(cmd)
        subprocess.run(cmd, shell=True)
        click.echo()
        click.echo(click.style("Create new user for export directory:", fg='bright_green'))
        click.echo("Directory:\t" + target_dir)
        if app:
            if app in ["RNAseq", "tRNAseq", "mRNAseq", "3mRNAseq"]:
                app = "RNAseq"
            click.echo("URL:\t" + url + "/3_Reports/analysis/Analysis_Report_" + app + ".html")
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
        contents = [l.rstrip() for l in f1.readlines()]
    for i,line in enumerate(contents):
        if "GPM_TITLE_NAME" in line:
            contents[i] = line.replace("GPM_TITLE_NAME", os.path.basename(export_dir))

    with open(os.path.join(export_dir, ".htaccess"), "w") as f2:
        for line in contents:
            print(line, file=f2)
    # Create user
    htpasswd_create_user(export_dir, os.path.join(export_URL, os.path.basename(export_dir)), 
                         user.lower(), "customized")

def get_gpmdata_path():
    return os.path.expanduser(os.getenv("GPMDATA", os.path.join(os.getenv("HOME"), "gpmdata")))

def get_gpmconfig(section, item):
    # Return the content in the config file. The user defined config has higher priority than the default config.
    gpmconfig = os.path.join(get_gpmdata_path(), "gpm.config")
    config = ConfigParser()
    config.read_file(codecs.open(gpmconfig, "r", "utf8"))
    gpmconfig = os.path.join(get_gpmdata_path(), "gpm.config.user")
    if os.path.exists(gpmconfig):
        config.read_file(codecs.open(gpmconfig, "r", "utf8"))
    return(config[section][item])

def get_config(config_name):
    cfg_path = os.path.join(get_gpmdata_path(), config_name+".user")
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(get_gpmdata_path(), config_name)
    return(cfg_path)