import logging
from os import environ, listdir
import shutil
import sys
from pkg_resources import resource_filename, get_distribution
import re
import renv.utils as utils
from renv import cookies
import yaml
from pathlib import Path
from cookiecutter.main import cookiecutter


class BaseRenvBuilder(object):
    """
The RenvBuilder class is a rework of the venv.EnvBuilder class.
The EnvBuilder class can be found here:
https://github.com/python/cpython/blob/3.6/Lib/venv/__init__.py

This class is meant to help facilitate the basic functionality of creating an
R environment.
"""

    def __init__(self, env_name=None, path=None, name=None, r_home=None, recommended_packages=True,
                 clear=False, upgrade=False, prompt=None, init=None, verbose=None):
        # Set up logger
        # Change level of logger based on verbose paramater.
        self.verbose = verbose
        if self.verbose:
            logging.basicConfig(format='[%(levelname)s | %(name)s - line %(lineno)d]: %(message)s')
            # Filter the debug logging
            logging.getLogger("renv").setLevel(logging.DEBUG)
        else:
            logging.basicConfig(format='%(levelname)s: %(message)s',
                                level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Set up cran variables
        self.cran_mirror = "https://cran.rstudio.com/"
        self.cranextra_mirror = "https://mirrors.nics.utk.edu/cran/"

        # Set up path to renv config directory
        self.path = Path(path).expanduser().absolute()
        self.name = name
        self.renv_path = self.path / name

        # Set up virtual environment class variables
        if env_name and r_home:
            self.env_name = env_name
            self.env_home = self.renv_path / "cran" / self.env_name

            # Set the class variables that represent the system's R installation
            self.r_home = Path(r_home)
            if not self.r_home.exists():
                raise FileNotFoundError("%s does not exist." % self.r_home)

            self.logger.debug("Target Installation:  %s" % str(self.r_home))
            self.logger.debug("Virtual Environment:  %s" % str(self.env_home))

            # Set boolean/None class variables
            self.clear = clear
            self.recommended_packages = recommended_packages
            self.upgrade = upgrade

            # Set up promtp
            if prompt:
                self.prompt = '(%s) ' % prompt
            else:
                self.prompt = '(%s) ' % self.env_name

        # Initialize renv if necessary
        self.cookie_jar = Path(resource_filename(cookies.__name__, ''))
        if init:
            if self.renv_path.exists():
                raise FileExistsError("The rinse path you have set already exists: %s" % self.renv_path)
            elif not self.renv_path.exists():
                self.initial_setup()
            elif not self.renv_path.exists():
                raise EnvironmentError("You have not initialized rinse yet.  Please run 'rinse init' to continue.")

    def initial_setup(self):
        self.logger.info("Initializing renv for the first time...")
        init_cookie = self.cookie_jar / Path("init")
        e_c = {
            "renv_init_dir": self.name
        }
        cookiecutter(str(init_cookie), no_input=True, extra_context=e_c, output_dir=str(self.path))


class LinuxRenvBuilder(BaseRenvBuilder):

    def __init__(self, env_name=None, path=None, name=None, r_home=None, bindir=None, libdir=None, mandir=None,
                 rincludedir=None, rdocdir=None, rsharedir=None, infodir=None, recommended_packages=True, clear=False,
                 upgrade=False, prompt=None, verbose=None):

        super().__init__(env_name=env_name, path=path, name=name, r_home=r_home,
                         recommended_packages=recommended_packages, clear=clear, upgrade=upgrade,
                         prompt=prompt, verbose=verbose)
        # ****************** SYSTEM R ****************
        #
        # Get installation directories.  These mimic parameters in source installation.  (./configure --help)
        # See https://cran.r-project.org/doc/manuals/R-admin.html#Installation for info on these directories.
        self.bindir = bindir
        if not self.bindir:
            self.bindir = self.r_home / "bin"
        self.libdir = libdir
        self.mandir = mandir
        if not self.mandir:
            self.mandir = self.r_home / "share" / "man"
        self.rincludedir = rincludedir
        self.rdocdir = rdocdir
        self.rsharedir = rsharedir
        self.infodir = infodir

        # Here LIBnn is usually ‘lib’, but may be ‘lib64’ on some 64-bit Linux systems
        # See previous link
        if sys.maxsize > 2**32:
            self.libnn = "lib64"
        else:
            self.libnn = "lib"
        if not self.libdir:
            self.libdir = self.r_home / self.libnn
        if not self.rincludedir:
            self.rincludedir = self.libdir / "R" / "include"
        if not self.rdocdir:
            self.rdocdir = self.libdir / "R" / "doc"
        if not self.rsharedir:
            self.rsharedir = self.libdir / "R" / "share"
        if not self.infodir:
            self.infodir = self.r_home / "info"

        # Start setting other variables.
        self.rlibrary = self.libdir / "R" / "library"

        # R version
        major, error = utils.system_r_call(rcmd_type="major", rscript=str(self.bindir / "Rscript"))
        # Minor Version
        minor, error = utils.system_r_call(rcmd_type="minor", rscript=str(self.bindir / "Rscript"))
        major = re.findall('"([^"]*)"', major)
        minor = re.findall('"([^"]*)"', minor)

        self.r_major_ver = major
        self.r_minor_ver = minor
        self.r_version = "%s.%s" % (str(major[0]), str(minor[0]))
        self.logger.debug("The target R version is %s." % self.r_version)

        # ****************** Virtual Environment R ****************
        self.usr_cfg_file = self.env_home / "renv.yaml"
        self.env_libdir = self.env_home / self.libnn
        self.env_bindir = self.env_home / "bin"
        self.env_mandir = self.env_home / "share" / "man"
        self.env_includedir = self.env_libdir / "R" / "include"
        self.env_docdir = self.env_libdir / "R" / "doc"
        self.env_sharedir = self.env_libdir / "R" / "share"
        self.env_infodir = self.env_home / "info"
        self.env_library = self.env_libdir / "R" / "library"

    def build_venv(self):
        self.create_env_dirs()
        self.create_etc_symlink()
        self.create_library_symlink()
        self.setup_templates()
        self.create_r_symlink()

    def create_env_dirs(self):
        self.logger.info("Creating renv directories...")
        env_lib_home = self.env_libdir / "R"
        sys_lib_home = self.libdir / "R"

        # create directories
        if not self.env_home.exists():
            self.env_home.mkdir()
            self.logger.debug(str(self.env_home))
        env_lib_home.mkdir(parents=True)  # make home and env_libdir
        self.logger.debug(str(env_lib_home))
        Path(env_lib_home / "etc").mkdir()
        self.logger.debug(str(env_lib_home / "etc"))
        Path(env_lib_home / "library").mkdir()
        self.logger.debug(str(env_lib_home / "library"))

        # create directory system links
        Path(env_lib_home / "bin").symlink_to(sys_lib_home / "bin")
        self.logger.debug(str(env_lib_home / "bin"))
        Path(env_lib_home / "modules").symlink_to(sys_lib_home / "modules")
        self.logger.debug(str(env_lib_home / "modules"))
        self.env_includedir.symlink_to(self.rincludedir)
        self.logger.debug(str(self.env_includedir))
        self.env_docdir.symlink_to(self.rdocdir)
        self.logger.debug(str(self.env_docdir))
        self.env_sharedir.symlink_to(self.rsharedir)
        self.logger.debug(str(self.env_sharedir))

        if Path(sys_lib_home / "tests").exists():
            Path(env_lib_home / "tests").symlink_to(sys_lib_home / "tests")
            self.logger.debug(str(env_lib_home / "tests"))
        if Path(self.mandir / "man1").exists():
            self.env_mandir.mkdir(parents=True)
            Path(self.env_mandir / "man1").symlink_to(self.mandir / "man1")
            self.logger.debug(str(self.env_mandir))
        if self.infodir.exists():
            self.env_infodir.symlink_to(self.infodir)
            self.logger.debug(str(self.env_infodir))

    def create_etc_symlink(self):
        env_lib_home = self.env_libdir / "R"
        sys_lib_home = self.libdir / "R"
        # create system link files
        etc_files = listdir(str(Path(sys_lib_home / "etc")))
        for file in etc_files:
            if file != "Rprofile.site":
                Path(env_lib_home / "etc" / file).symlink_to(sys_lib_home / "etc" / file)
                self.logger.debug(str(env_lib_home / "etc" / file))

    def create_library_symlink(self):
        # Get base packages from system R
        base_pkgs, error = utils.system_r_call(rcmd_type="base", rscript=str(self.bindir / "Rscript"))
        base_pkgs = base_pkgs.split(" ")
        self.logger.debug("Using base packages...")
        # Get recommended packages from system R
        if self.recommended_packages:
            recommended_pkgs, error = utils.system_r_call(rcmd_type="recommended", rscript=str(self.bindir / "Rscript"))
            recommended_pkgs = recommended_pkgs.split(" ")
            self.logger.debug("Using recommended packages...")
            pkgs = base_pkgs + recommended_pkgs
        else:
            pkgs = base_pkgs
        # symlink the packages to the environment
        for pkg in pkgs:
            self.logger.debug(str(pkg))
            pkg_path = self.rlibrary / pkg
            env_pkg_path = self.env_library / pkg
            env_pkg_path.symlink_to(pkg_path)

    def setup_templates(self):
        self.logger.debug("Setting up templated files...")
        activator_cookie = self.cookie_jar / 'posix'
        e_c = {
            "dirname": "bin",
            "__VENV_DIR__": str(self.env_home),
            "__VENV_NAME__": self.env_name,
            "__VENV_PROMPT__": self.prompt,
            "__VENV_BIN_NAME__": "bin",  # Why???
            "__VENV_R__": str(self.env_bindir / "R"),
            "__VENV_RSCRIPT__": str(self.env_bindir / "Rscript"),
            "__R_VERSION__": self.r_version,
            "__CRAN_MIRROR__": self.cran_mirror,
            "__CRANEXTRA_MIRROR__": self.cranextra_mirror,
            "__R_LIBS_USER__": str(self.env_library),
            "__R_LIBS_SITE__": str(self.env_library),
            "__R_HOME__": str(self.env_home),
            "__R_INCLUDE_DIR__": str(self.env_includedir),
            "__R_DOC_DIR__": str(self.env_docdir),
            "__R_SHARE_DIR__": str(self.env_sharedir)
        }
        cookiecutter(str(activator_cookie), no_input=True, extra_context=e_c, output_dir=self.env_home)
        shutil.move(str(self.env_bindir / "Rprofile.site"), str(self.env_libdir / "R" / "etc"))

    def create_r_symlink(self):
        self.logger.debug("Setting up R executables...")
        # Set up symlinks of r executables
        for suffix in ("R", "Rscript"):
            env_exe = self.env_bindir / suffix
            sys_exe = self.bindir / suffix
            if not env_exe.exists():
                if sys_exe.exists():
                    env_exe.symlink_to(sys_exe)
                    self.logger.debug(suffix)
                else:
                    raise FileNotFoundError("%s does not exist." % str(sys_exe))
            else:
                raise FileExistsError("%s already exists." % env_exe)


class MacRenvBuilder(BaseRenvBuilder):

    def __init__(self):
        raise NotImplementedError("Creating virtual environments for R with renv on MacOS is not supported at this "
                                  "time.")


class WindowsRenvBuilder(BaseRenvBuilder):

    def __init__(self):
        raise NotImplementedError("Creating virtual environments for R with renv on Windows is not supported at this "
                                  "time.")
