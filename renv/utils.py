import os
import subprocess as sp
from shutil import rmtree

def get_r_path():
    """
    Get current R installed path in Linux
    # TODO make this function cross-platform
    :return: path to R
    """
    sp_out = sp.run(["which R"], shell=True, capture_output=True, encoding="utf8")
    if sp_out.returncode:
        raise Exception("Could not get the default R path. Is R installed?")

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
    sp_out = sp.run(["echo $HOME"], shell=True, capture_output=True, encoding="utf8")
    return sp_out.stdout.strip()

def get_beri_path(has_root_access=False):
    """
    Get the default R environment path
    # TODO make this function cross-platform
    :param has_root_access: whether user has root access in Linux.
    :return: path to beRi_envs, inclusive.
    """
    if has_root_access:
        return os.path.join(get_r_installed_root(), "beRi_envs")
    else:
        return os.path.join(get_user_home_dir(), "beRi_envs")

def get_default_env_path(env_name):
    """
    Get default environment path for the given environment
    :param env_name: name of the R environment
    :return: path to the environment with the default root path
    """
    return os.path.join(get_beri_path(), env_name)


def create_directory(directory, clear=False):
    """
    Create directory if it does not exist yet.
    :param clear: whether to clear the directory if it already exists
    :param directory: path of the directory
    :return: None
    """

    if os.path.exists(directory):
        if clear:
            rmtree(directory)
        else:
            raise Exception("Environment directory " + directory +
                            " already exists. Set clear to True to erase the original directory.")
    elif os.path.islink(directory) or os.path.isfile(directory):
        raise ValueError("Unable to create directory '%r" % directory + "' for the new environment.")
    else:
        os.makedirs(directory)
