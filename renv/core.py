from venv import EnvBuilder
import logging
from os import environ, listdir
import shutil
import subprocess
import sys
import types
import yaml
import renv.utils as utils
from pkg_resources import resource_filename
from renv import cookies
from pathlib import Path
from cookiecutter.main import cookiecutter
logger = logging.getLogger(__name__)

__DEFAULT_CONFIG__ = {
    "CRAN_MIRROR": "https://cran.rstudio.com/",
    "CRANEXTRA_MIRROR": "https://mirrors.nics.utk.edu/cran/",
    "STANDARD_PKG_LIST": {
        "BiocInstaller": "Bioconductor",
        "devtools": "Devtools"
    },
    "REPRODUCIBLE_WORKFLOW_PKG_LIST": {
        "tidyverse": "Tidyverse"
    }
}


class BaseRenvBuilder(object):
    """
The RenvBuilder class is a rework of the venv.EnvBuilder class.
The EnvBuilder class can be found here:
https://github.com/python/cpython/blob/3.6/Lib/venv/__init__.py

This class is meant to help facilitate the basic functionality of creating an
R environment.
"""

    def __init__(self, env_name=None, path=None, name=None, r_home=None, recommended_packages=True,
                 clear=False, symlinks=False, upgrade=False, prompt=None, init=None):
        # Set up path to renv config directory
        self.path = Path(path).expanduser().absolute()
        self.name = name
        self.renv_path = self.path / name

        # Set up virtual environment class variables
        self.env_name = env_name
        self.env_home = self.renv_path / "cran" / self.env_name

        # Set the class variables that represent the system's R installation
        self.r_home = Path(r_home)
        self.R_version = self.r_home.stem

        # Set boolean/None class variables
        self.clear = clear
        self.recommended_packages = recommended_packages
        self.symlinks = symlinks
        self.upgrade = upgrade
        if prompt:
            self.prompt = '(%s) ' % prompt
        else:
            self.prompt = '(%s) ' % self.env_name

        self.cookie_jar = Path(resource_filename(cookies.__name__, ''))
        if init:
            if self.renv_path.exists():
                raise FileExistsError("The rinse path you have set already exists: %s" % self.renv_path)
            elif not self.renv_path.exists():
                self.initial_setup()
            elif not self.renv_path.exists():
                raise EnvironmentError("You have not initialized rinse yet.  Please run 'rinse init' to continue.")

    def initial_setup(self):
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
        env_lib_home = self.env_libdir / "R"
        sys_lib_home = self.libdir / "R"

        # create directories
        if not self.env_home.exists():
            self.env_home.mkdir()
        env_lib_home.mkdir(parents=True)  # make home and env_libdir
        Path(env_lib_home / "etc").mkdir()
        Path(env_lib_home / "library").mkdir()

        # create directory system links
        Path(env_lib_home / "bin").symlink_to(sys_lib_home / "bin")
        Path(env_lib_home / "module").symlink_to(sys_lib_home / "modules")
        self.env_includedir.symlink_to(self.rincludedir)
        self.env_docdir.symlink_to(self.rdocdir)
        self.env_sharedir.symlink_to(self.rsharedir)

        if Path(sys_lib_home / "tests").exists():
            Path(env_lib_home / "tests").symlink_to(sys_lib_home / "tests")
        if Path(self.mandir / "man1").exists():
            self.env_mandir.symlink_to(self.mandir)
        if self.infodir.exists():
            self.env_infodir.symlink_to(self.infodir)

    def create_etc_symlink(self):
        env_lib_home = self.env_libdir / "R"
        sys_lib_home = self.libdir / "R"
        # create system link files
        etc_files = listdir(str(Path(sys_lib_home / "etc")))
        for file in etc_files:
            if file != "Rprofile.site":
                Path(env_lib_home / "etc" / file).symlink_to(sys_lib_home / "etc" / file)



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
        """
        super().__init__(system_site_packages=system_site_packages, clear=clear,
                         symlinks=symlinks, upgrade=upgrade, prompt=prompt)
        del self.with_pip
        if r_path is None:
            r_path = utils.get_r_installed_root()
        self.r_path = r_path
        self.r_bin_path = r_bin_path
        self.r_lib_path = r_lib_path
        self.r_include_path = r_include_path
        self.clear = clear
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
            env_dir = utils.get_beri_path()
            if env_name:
                env_dir = os.path.join(env_dir, env_name)
            else:
                Exception("Please provide the environment name.")

        context = self.ensure_directories(env_dir)
        # TODO-ROB: pip will eventually be beRi
        # See issue 24875. We need system_site_packages to be False
        # until after pip is installed.
        true_system_site_packages = self.system_site_packages
        self.system_site_packages = False
        context.config_dict = self.create_configuration(context)
        # self.setup_r(context)
        # TODO-ROB: pip will eventually be beRi
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

        print("\nEnvironment created in " + env_dir + "\n")

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
        context.R_version = os.path.split(self.r_path)[1]
        if self.r_bin_path:
            context.abs_R_exe = os.path.join(self.r_bin_path, r_exe)
            context.abs_R_script = os.path.join(self.r_bin_path, r_script)
        else:
            context.abs_R_exe = os.path.join(self.r_path, "bin", r_exe)
            context.abs_R_script = os.path.join(self.r_path, "bin", r_script)
        context.abs_R_path = self.r_path
        logging.info(f"System R(version):  {self.r_path}({context.R_version})")

        # Begin with R-Environment R files/paths
        # Continue with system R files/paths
        if sys.platform == 'win32':  # Windows
            r_env_home = env_dir
            r_abs_home = self.r_path
            r_env_include = "include"
            r_abs_include = "include"
        else:  # Linux
            r_env_home = os.path.join(env_dir, 'lib', "R")
            if self.r_lib_path:
                r_abs_home = os.path.join(self.r_lib_path, "R")
            else:
                r_abs_home = os.path.join(self.r_path, 'lib', "R")
            r_env_include = os.path.join(r_env_home, "include")
            if self.r_include_path:
                r_abs_include = self.r_include_path
            else:
                r_abs_include = os.path.join(self.r_path, "include")
        # Issue 21197: create lib64 as a symlink to lib on 64-bit non-OS X POSIX
        utils.create_directory(r_env_home, self.clear)
        
        # Create symlink to R 
        if (sys.maxsize > 2**32) and (os.name == 'posix') and (sys.platform != 'darwin'):
            os.mkdir(os.path.join(env_dir, 'lib64'))
            link_path = os.path.join(env_dir, 'lib64', 'R')
            if not os.path.exists(link_path):   # Issue #21643
                os.symlink(r_env_home, link_path)
        
        # Create other symbolic links in lib/R/
        utils.create_symlink(
            os.path.join(utils.get_r_installed_root(), "lib", "R"),
            os.path.join(env_dir, "lib", "R"), 
            ["bin", "etc", "lib", "modules", "share", "include"])
        
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
        context.env_bin_path = binpath = os.path.join(env_dir, binname)
        context.bin_path = binpath
        context.env_R_exe = os.path.join(binpath, r_exe)
        context.env_R_script = os.path.join(binpath, r_script)
        utils.create_directory(context.env_R_libs, self.clear)
        logging.info(f"Environment R:  {r_env_home}")
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
            with open(path, 'r', encoding='utf-8')as f:
                user_config = yaml.load(f)
        else:
            user_config = {}

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
                    Rcmd = f"{context.abs_R_script} " \
                           f"-e \'base::cat(rownames(installed.packages(priority=\"recommended\")))\'"
                    recommended_pkgs = subprocess.Popen([Rcmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                                        shell=True, encoding='utf-8')
                    error = recommended_pkgs.stderr.readlines()
                    out = recommended_pkgs.stdout.readlines()
                    recommended_pkgs.wait()
                    recommended_pkgs = out[0].split(" ")
                # Get a list of the base packages for this version of R
                if self.base_packages:
                    Rcmd = f"{context.abs_R_script} " \
                           f"-e \'base::cat(rownames(installed.packages(priority=\"base\")))\'"
                    base_pkgs = subprocess.Popen([Rcmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                                        shell=True, encoding='utf-8')
                    error = base_pkgs.stderr.readlines()
                    out = base_pkgs.stdout.readlines()
                    base_pkgs.wait()
                    base_pkgs = out[0].split(" ")
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
            config_dict["R_VERSION"] = context.R_version
            # Package lists
            config_dict.update(__DEFAULT_CONFIG__)
            pkg_lists = self.format_pkg_list(config_dict)
            config_dict.update(pkg_lists)
            config_dict.update(user_config)
            logging.info(f"Config Dictionary:  {config_dict}")

            # Dump the configuration dictionary to the YAML file in the R environment HOME
            yaml.dump(config_dict, f, default_flow_style=False)
        # TODO-ROB:  This would only be apply under Windows.  This is called in setup_python(r)
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
            # TODO-ROB: Build Windows version
            raise OSError("renv is only currently working for some POISIX systems.")
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
            "__R_HOME__": context.config_dict["R_ENV_HOME"],
            "__R_INCLUDE_DIR__": context.config_dict["R_INCLUDE_DIR"],
            "__STANDARD_PKG_LIST__": context.config_dict["STANDARD_PKG_LIST"],
            "__REPRODUCIBLE_WORKFLOW_PKG_LIST__": context.config_dict["REPRODUCIBLE_WORKFLOW_PKG_LIST"]
        }
        env_dir = context.env_dir
        cookiecutter(str(activator_cookie), no_input=True, extra_context=e_c, output_dir=context.env_dir)

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
                    pkg_list_string = f"{pkg_list_string}{v}=\"{pkg_dict[v]}\""
                else:
                    sep = ", "
                    pkg_list_string = f"{pkg_list_string}{v}=\"{pkg_dict[v]}\"{sep}"

            pkg_list_string = f"list({pkg_list_string})"
            fmtd_list[list_name] = pkg_list_string

        return fmtd_list

    # def install_r(self):
    #     # New: install specified version of R in the R environment.
    #     pass
    #
    # def setup_r_profile(self, context):
    #     # New
    #     pass
    #
    # def setup_r_environ(self):
    #     # New
    #     pass
