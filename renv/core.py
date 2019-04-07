from venv import EnvBuilder
import logging
import os
from os import environ, listdir
import shutil
import subprocess
import sys
import types
from pkg_resources import resource_filename, get_distribution
from pprint import pprint, pformat
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
                 clear=False, symlinks=False, upgrade=False, prompt=None, init=None, verbose=None):
        # Set up logger
        # Change level of logger based on verbose paramater.
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
        self.symlinks = symlinks
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
                 rincludedir=None, rdocdir=None, rsharedir=None, infodir=None, recommended_packages=True, clear=False, symlinks=False,
                 upgrade=False, prompt=None):

        super().__init__(env_name=env_name, path=path, name=name, r_home=r_home,
                         recommended_packages=recommended_packages, clear=clear, symlinks=symlinks, upgrade=upgrade,
                         prompt=prompt)
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
        self.env_library = self.libdir / "R" / "library"

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
            self.env_mandir.symlink_to(self.mandir)
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
            "__R_LIBS_USER__": self.env_library,
            "__R_LIBS_SITE__": self.env_library,
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


class RenvBuilder(EnvBuilder):

    def __init__(self, r_path=None, r_bin_path=None, r_lib_path=None, r_include_path=None, system_site_packages=False,
                 recommended_packages=True, clear=False, symlinks=False, upgrade=False, prompt=None):
        """
        :param r_path:  This is the root directory of the R installation that's being
        used to create the virtual environment.
        :param r_bin_path:  This is the bin directory of the R installation that's being
        used to create the virtual environment.
        :param r_lib_path:  This is the lib directory of the R installation that's being
        used to create the virtual environment.
        :param r_include_path:  This is the include directory of the R installation that's
        being used to create the virtual environment.
        :param system_site_packages:  A switch for including the r_path library packages
        in the env.
        :param recommended_packages:  A switch for including the recommended packages in
        the env.
        :param clear:  A switch for clearing the environment directory if it exists.
        :param symlinks:  A switch for using system links or not.
        :param upgrade:  A switch for upgrading vs creating an environment.
        :param prompt:  The prompt prefix can be customized with this parameter.
        :param prompt:  A switch for verbosity level of cli output.
        """
        super().__init__(system_site_packages=system_site_packages, clear=clear,
                         symlinks=symlinks, upgrade=upgrade)
        self.prompt = prompt
        del self.with_pip
        if r_path is None:
            r_path = utils.get_r_installed_root()
        self.r_path = r_path
        self.r_bin_path = r_bin_path
        self.r_lib_path = r_lib_path
        self.r_include_path = r_include_path
        self.clear = clear
        self.verbose = verbose

        # Set up logger
        # Change level of logger based on verbose paramater.
        if self.verbose:
            logging.basicConfig(format='[%(levelname)s | %(name)s - line %(lineno)d]: %(message)s')
            # Filter the debug logging
            logging.getLogger("renv").setLevel(logging.DEBUG)
        else:
            logging.basicConfig(format='%(levelname)s: %(message)s',
                                level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        if self.system_site_packages:
            self.base_packages = False
            self.recommended_packages = False
        else:
            self.base_packages = True
            self.recommended_packages = recommended_packages

    def create(self, env_dir, env_name=None):
        """
        Create a virtual environment in a directory.
        :param env_dir: The target directory to create an environment in.
        """
        if env_dir:
            env_dir = os.path.abspath(env_dir)
        else:
            env_dir = utils.get_renv_path()
            if env_name:
                env_dir = os.path.join(env_dir, env_name)
            else:
                self.logger.exception("Please provide the environment name.")

        context = self.ensure_directories(env_dir)
        # TODO: pip will eventually be beRi
        # See issue 24875. We need system_site_packages to be False
        # until after pip is installed.
        true_system_site_packages = self.system_site_packages
        self.system_site_packages = False
        context.config_dict = self.create_configuration(context)
        # self.setup_r(context)
        # TODO: pip will eventually be beRi
        # if self.with_pip:
        #     self._setup_pip(context)
        if not self.upgrade:
            self.install_scripts(context)
            self.setup_r(context)
            self.post_setup(context)
        if true_system_site_packages:
            # We had set it to False before, now
            # restore it and rewrite the configuration
            self.setup_r(context)
            self.system_site_packages = True
            self.create_configuration(context)

        self.logger.info("Environment created at %s" % env_dir)

    def ensure_directories(self, env_dir):
        """
        Creates the context and directories of the R environment.
        The context contains all of the paths used in the setup.

        :param env_dir:  The directory used for the environment.
        """

        user_config = os.path.join(env_dir, "renv.yaml")

        # Create the context for the virtual environment
        context = types.SimpleNamespace()
        context.user_config = user_config
        context.env_dir = env_dir
        context.env_name = os.path.split(env_dir)[1]
        prompt = self.prompt if self.prompt is not None else context.env_name
        context.prompt = '(%s) ' % prompt
        utils.create_directory(env_dir, self.clear)

        # System R files/paths
        r_exe = "R"
        r_script = "Rscript"
        context.R_exe = r_exe
        context.R_script = r_script

        if self.r_bin_path:
            context.abs_R_exe = os.path.join(self.r_bin_path, r_exe)
            context.abs_R_script = os.path.join(self.r_bin_path, r_script)
        else:
            context.abs_R_exe = os.path.join(self.r_path, "bin", r_exe)
            context.abs_R_script = os.path.join(self.r_path, "bin", r_script)
        context.abs_R_path = self.r_path

        # Get the version of R
        # Major Version
        major, error = utils.system_r_call(rcmd_type="major", context=context)
        # Minor Version
        minor, error = utils.system_r_call(rcmd_type="minor", context=context)

        major = re.findall('"([^"]*)"', major)
        minor = re.findall('"([^"]*)"', minor)
        context.R_version = "%s.%s" % (str(major[0]), str(minor[0]))
        self.logger.debug("The system R version is %s" % context.R_version)

        # Begin with R-Environment R files/paths
        # Continue with system R files/paths
        if sys.platform == 'win32':  # Windows
            r_env_home = env_dir
            r_abs_home = self.r_path
            r_env_include = "include"
            r_abs_include = "include"
            r_env_doc = "doc"
            r_env_share = "share"
        else:  # Linux
            logging.debug("System Platform: %s" % sys.platform)
            r_env_home = os.path.join(env_dir, 'lib', "R")
            if self.r_lib_path:
                r_abs_home = os.path.join(self.r_lib_path, "R")
            else:
                if sys.maxsize > 2**32:
                    r_abs_home = os.path.join(self.r_path, 'lib64', "R")
                else:
                    r_abs_home = os.path.join(self.r_path, 'lib', "R")
            r_env_include = os.path.join(r_env_home, "include")
            r_env_share = os.path.join(r_env_home, "share")
            r_env_doc = os.path.join(r_env_home, "doc")
            if self.r_include_path:
                r_abs_include = self.r_include_path
            else:
                r_abs_include = os.path.join(self.r_path, "include")
        # Issue 21197: create lib64 as a symlink to lib on 64-bit non-OS X POSIX
        utils.create_directory(r_env_home, self.clear)

        r_lib_path = os.path.join(self.r_path, "lib", "R")
        # Create symlink to R
        if (sys.maxsize == 2**63-1) and (os.name == 'posix') and (sys.platform != 'darwin'):
            os.mkdir(os.path.join(env_dir, 'lib64'))
            link_path = os.path.join(env_dir, 'lib64', 'R')
            r_lib_path = os.path.join(self.r_path, "lib64", "R")
            if not os.path.exists(link_path):   # Issue #21643
                os.symlink(r_env_home, link_path)
                self.logger.debug("Symlink created in %s" % link_path)

        # Create other symbolic links in lib/R/
        utils.create_symlink(
            r_lib_path,
            os.path.join(env_dir, "lib", "R"),
            ["bin", "etc", "lib", "modules", "share", "include", "doc", "tests"])

        binname = 'bin'
        r_env_libs = os.path.join(r_env_home, 'library')
        r_abs_libs = os.path.join(r_abs_home, 'library')
        context.bin_name = binname
        context.packrat_home = os.path.join(env_dir, 'projects')
        context.env_R_home = r_env_home
        context.abs_R_home = r_abs_home
        context.env_R_libs = r_env_libs
        context.abs_R_libs = r_abs_libs
        context.env_R_include = os.path.join(env_dir, r_env_include)
        context.env_R_doc = os.path.join(env_dir, r_env_doc)
        context.env_R_share = os.path.join(env_dir, r_env_share)
        context.env_bin_path = binpath = os.path.join(env_dir, binname)
        context.bin_path = binpath
        context.env_R_exe = os.path.join(binpath, r_exe)
        context.env_R_script = os.path.join(binpath, r_script)
        utils.create_directory(context.env_R_libs, self.clear)
        self.logger.info("Environment R:  %s" % r_env_home)
        return context

    def create_configuration(self, context):
        """
        Create and/or use a configuration file indicating where the environment's R
        was copied from, and whether the system site-packages should be made
        available in the environment.

        :param context: The information for the environment creation request
                        being processed.
        """
        config_dict = dict()
        recommended_pkgs = list()
        base_pkgs = list()
        copier = self.symlink_or_copy
        path = context.user_config
        # Get the user provided YAML config if it exists
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                user_config = yaml.load(f)
            f.close()
            formatted_user_config = pformat(user_config)
            self.logger.debug("User configuration file imported.")
            self.logger.debug("User configuration: %s" % formatted_user_config)
        else:
            user_config = {}
            self.logger.debug("User configuration will be default.")

        # Open and overwrite YAML config
        with open(path, 'w', encoding='utf-8') as f:
            # Append system R_LIBS_USER if desired
            if self.system_site_packages:
                sep = ";" if sys.platform == "win32" else ":"
                config_dict["R_LIBS_USER"] = "%s%s%s" % (context.env_R_libs, sep, context.abs_R_libs)
            else:
                config_dict["R_LIBS_USER"] = context.env_R_libs
                # Get a list of the recommended packages for this version of R
                if self.recommended_packages:
                    recommended_pkgs, error = utils.system_r_call(rcmd_type="recommended", context=context)
                    recommended_pkgs = recommended_pkgs.split(" ")
                    self.logger.debug("Recommended pkgs are: %s" % recommended_pkgs)
                # Get a list of the base packages for this version of R
                if self.base_packages:
                    base_pkgs, error = utils.system_r_call(rcmd_type="base", context=context)
                    base_pkgs = base_pkgs.split(" ")
                    self.logger.debug("Base pkgs are: %s" % base_pkgs)
                # Create a list of all the packages to use
                pkgs = recommended_pkgs + base_pkgs
                # TODO-config: This may need to be separate for windows vs linux
                # Copy the packages to the environment
                for pkg in pkgs:
                    abs_pkg_path = os.path.join(context.abs_R_libs, pkg)
                    env_pkg_path = os.path.join(context.env_R_libs, pkg)
                    copier(abs_pkg_path, env_pkg_path)
                    if not os.path.islink(env_pkg_path):
                        os.chmod(env_pkg_path, 0o755)

            # Add more variables
            config_dict["R_ENV_HOME"] = context.env_R_home
            config_dict["R_ABS_HOME"] = context.abs_R_home
            config_dict["R_INCLUDE_DIR"] = context.env_R_include
            config_dict["R_DOC_DIR"] = context.env_R_doc
            config_dict["R_SHARE_DIR"] = context.env_R_share
            config_dict["R_VERSION"] = context.R_version

            # Package lists
            config_dict.update(__DEFAULT_CONFIG__)
            pkg_lists = self.format_pkg_list(config_dict)
            config_dict.update(pkg_lists)
            config_dict.update(user_config)
            formatted_config_dict = pformat(config_dict)
            self.logger.debug("Config Dictionary:  %s" % formatted_config_dict)

            # Dump the configuration dictionary to the YAML file in the R environment HOME
            yaml.dump(config_dict, f, default_flow_style=False)
        # TODO:  This would only be apply under Windows.  This is called in setup_python(r)
        # if os.name == 'nt':
        #     def include_binary(self, f):
        #         if f.endswith(('.pyd', '.dll')):
        #             result = True
        #         else:
        #             result = f.startswith('python') and f.endswith('.exe')
        #         return result
        return config_dict

    def setup_r(self, context):
        """
       Set up a R executable in the environment.
       :param context: The information for the environment creation request
                       being processed.
       """
        env_bin = context.env_bin_path
        env_R = context.env_R_exe
        env_R_script = context.env_R_script
        copier = self.symlink_or_copy
        copier(context.abs_R_exe, env_R)
        copier(context.abs_R_script, env_R_script)
        dirname = context.abs_R_path
        if os.name != 'nt':
            if not os.path.islink(env_R):
                os.chmod(env_R, 0o755)
            # for suffix in ('python', 'python3'):
            for suffix in ('R', 'Rscript'):
                exe_path = os.path.join(env_bin, suffix)
                if not os.path.exists(exe_path):
                    abs_exe_path = os.path.join(dirname, "bin", suffix)
                    # Issue 18807: make copies if
                    # symlinks are not wanted
                    copier(abs_exe_path, exe_path, relative_symlinks_ok=True)
                    if not os.path.islink(exe_path):
                        os.chmod(exe_path, 0o755)
        else:
            # TODO: Build Windows version
            raise OSError("renv is only currently working for some POSIX systems.")
            # subdir = 'DLLs'
            # include = self.include_binary
            # files = [f for f in os.listdir(dirname) if include(f)]
            # for f in files:
            #     src = os.path.join(dirname, f)
            #     dst = os.path.join(binpath, f)
            #     if dst != context.env_exe:  # already done, above
            #         copier(src, dst)
            # dirname = os.path.join(dirname, subdir)
            # if os.path.isdir(dirname):
            #     files = [f for f in os.listdir(dirname) if include(f)]
            #     for f in files:
            #         src = os.path.join(dirname, f)
            #         dst = os.path.join(binpath, f)
            #         copier(src, dst)
            # # copy init.tcl over
            # for root, dirs, files in os.walk(context.python_dir):
            #     if 'init.tcl' in files:
            #         tcldir = os.path.basename(root)
            #         tcldir = os.path.join(context.env_dir, 'Lib', tcldir)
            #         if not os.path.exists(tcldir):
            #             os.makedirs(tcldir)
            #         src = os.path.join(root, 'init.tcl')
            #         dst = os.path.join(tcldir, 'init.tcl')
            #         shutil.copyfile(src, dst)
            #         break

    def install_scripts(self, context):
        """
        Install scripts into the created environment from a directory.
        :param context: The information for the environment creation request
                        being processed.
        :param path:    Absolute pathname of a directory containing script.
                        Scripts in the 'common' subdirectory of this directory,
                        and those in the directory named for the platform
                        being run on, are installed in the created environment.
                        Placeholder variables are replaced with environment-
                        specific values.
        """
        # Get the extra_context for the cookiecutter call
        cookie_jar = Path(resource_filename(cookies.__name__, ''))
        activator_cookie = cookie_jar / Path(os.name)
        e_c = {
            "dirname": "bin",
            "__VENV_DIR__": context.env_dir,
            "__VENV_NAME__": context.env_name,
            "__VENV_PROMPT__": context.prompt,
            "__VENV_BIN_NAME__": context.bin_name,
            "__VENV_R__": context.env_R_exe,
            "__VENV_RSCRIPT__": context.env_R_script,
            "__R_VERSION__": context.config_dict["R_VERSION"],
            "__CRAN_MIRROR__": context.config_dict["CRAN_MIRROR"],
            "__CRANEXTRA_MIRROR__": context.config_dict["CRANEXTRA_MIRROR"],
            "__R_LIBS_USER__": context.config_dict["R_LIBS_USER"],
            "__R_LIBS_SITE__": context.config_dict["R_LIBS_USER"],
            "__R_HOME__": context.config_dict["R_ENV_HOME"],
            "__R_INCLUDE_DIR__": context.config_dict["R_INCLUDE_DIR"],
            "__R_DOC_DIR__": context.config_dict["R_DOC_DIR"],
            "__R_SHARE_DIR__": context.config_dict["R_SHARE_DIR"],
            "__STANDARD_PKG_LIST__": context.config_dict["STANDARD_PKG_LIST"],
            "__REPRODUCIBLE_WORKFLOW_PKG_LIST__": context.config_dict["REPRODUCIBLE_WORKFLOW_PKG_LIST"]
        }
        env_dir = context.env_dir
        cookiecutter(str(activator_cookie), no_input=True, extra_context=e_c,
                     output_dir=env_dir)

    def format_pkg_list(self, config_dict):
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

