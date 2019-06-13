import os
import sys
import subprocess as sp
from shutil import rmtree
from subprocess import TimeoutExpired
import renv
import logging

logger = logging.getLogger(__name__)


def get_system_venv():
    if os.name == "posix":
        if sys.platform == "darwin":
            renv.MacRenvBuilder()
        elif "linux" in str(sys.platform):
            return renv.LinuxRenvBuilder
        else:
            logger.error("renv does not support %s operating system at this time." % sys.platform)
    elif os.name == "nt":
        if sys.platform == "win32":
            renv.WindowsRenvBuilder()
        else:
            logger.error("renv does not support %s operating system at this time." % sys.platform)


def get_r_path():
    """
    Get current R installed path in Linux
    # TODO make this function cross-platform
    :return: path to R
    """
    sp_out = sp.run(["which R"], shell=True, stdout=sp.PIPE, encoding="utf8")
    if sp_out.returncode:
        logger.exception("Could not get the default R path. Is R installed?")

    return sp_out.stdout.strip()


def get_r_installed_root():
    """
    Get the installed root of R (without /bin/R
    :return: path to root where R is installed
    """

    r_path = get_r_path()
    return os.path.dirname(os.path.dirname(r_path))  # remove /bin/R


def get_user_home_dir():
    """
    Get home directory in Linux where users can create directory.
    # TODO make this function cross-platform
    :return: None
    """
    sp_out = os.environ['HOME']
    return sp_out.strip()


def get_renv_path(has_root_access=False):
    """
    Get the default R environment path
    # TODO make this function cross-platform
    :param has_root_access: whether user has root access in Linux.
    :return: path to .renv, inclusive.
    """
    if has_root_access:
        return os.path.join(get_r_installed_root(), ".renv")
    else:
        return os.path.join(get_user_home_dir(), ".renv")


def create_directory(directory, clear=False):
    """
    Create directory if it does not exist yet.
    :param clear: Clear the directory if it already exists.
    :param directory: path of the directory
    :return: None
    """
    if os.path.exists(directory):
        if clear:
            rmtree(directory)
            logger.debug("%s has been deleted." % directory)
        else:
            logger.error("Environment directory %s exists. Set clear to True to delete the original directory." % directory)
    elif os.path.islink(directory) or os.path.isfile(directory):
        logger.error(ValueError("Unable to create directory '%r" % directory + "' for the new environment."))
    else:
        os.makedirs(directory)
        logger.debug("%s has been created." % directory)


def create_symlink(src, dst, subfolders=[]):
    """
    Create symlink in the dst folder from the src folder.
    :param src: source folder
    :param dst: desitnation foler
    :param subfolders: symlink to be created for these subfolders in src specifically
    :return: None
    """

    if len(subfolders) == 0:
        os.symlink(src, dst, target_is_directory=True)
    else:
        for subfolder in subfolders:
            src_folder = os.path.join(src, subfolder)
            dst_folder = os.path.join(dst, subfolder)
            if not os.path.exists(src_folder):
                logger.warning("Cannot create symlink from " + src_folder)
            elif not os.path.exists(dst_folder):
                logger.warning("Cannot create symlink at " + dst_folder)
            os.symlink(src_folder, dst_folder, target_is_directory=True)


def system_r_call(rcmd_type, rscript):
    """
    Call the current R with system calls in order to obtain specific types
    of information.
    :param rcmd_type:  A string that designates the R command to use in the system call
    :param rscript:  The absolute path to the desired Rscript exe.
    :return:  Returns the stdout and stderr from the system call.
    """

    if rcmd_type == "major":
        rcmd = "%s -e \'R.version$major\'" % rscript
    elif rcmd_type == "minor":
        rcmd = "%s -e \'R.version$minor\'" % rscript
    elif rcmd_type == "base":
        rcmd = "%s -e \'base::cat(rownames(installed.packages(priority=\"base\")))\'" % rscript
    elif rcmd_type == "recommended":
        rcmd = "%s -e \'base::cat(rownames(installed.packages(priority=\"recommended\")))\'" % rscript

    recommended_pkgs = sp.Popen([rcmd], stderr=sp.PIPE, stdout=sp.PIPE, shell=True, encoding='utf-8')

    try:
        stdout, stderr = recommended_pkgs.communicate(timeout=15)
    except TimeoutExpired:
        recommended_pkgs.kill()
        stdout, stderr = recommended_pkgs.communicate()

    return stdout, stderr


def format_pkg_list(config_dict):
    """
    Takes the YAML configuration information and parses/formats the R
    package list for use with an "Rscript -e **" call.
    :param config_dict:  The configuration dictionary created with the YAML file.
    """
    config_dict = {k: v for k, v in config_dict.items() if "PKG_LIST" in k}
    fmtd_list = dict()

    for list_name in config_dict:
        pkg_dict = config_dict[list_name]
        pkg_list_count = len(pkg_dict) - 1
        pkg_list_string = ""
        for k, v in enumerate(pkg_dict):
            if k == pkg_list_count:
                pkg_list_string = "%s%s=\"%s\"" % (pkg_list_string, v, pkg_dict[v])
            else:
                sep = ", "
                pkg_list_string = "%s%s=\"%s\"%s" % (pkg_list_string, v, pkg_dict[v], sep)

        pkg_list_string = "list(%s)" % pkg_list_string
        fmtd_list[list_name] = pkg_list_string

    return fmtd_list
