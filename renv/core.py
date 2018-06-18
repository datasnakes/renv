from venv import EnvBuilder
import logging
import os
import shutil
import subprocess
import sys
import types
import yaml
logger = logging.getLogger(__name__)

__DEFAULT_CONFIG__ = {
    "CRAN_MIRROR": "https://cran.rstudio.com/",
    "CRANEXTRA_MIRROR": "https://mirrors.nics.utk.edu/cran/",
    "STANDARD_PKG_LIST": {
        "BiocInstaller": "Bioconductor",
        "devtools": "Devtools"
    }
}


class RenvBuilder(EnvBuilder):
    """
    The RenvBuilder class is a giant rework of the venv.EnvBuilder class.
    The EnvBuilder class can be found here:
    https://github.com/python/cpython/blob/3.6/Lib/venv/__init__.py

    This initial skeleton class includes all of the methods that will need
    to be reworked for R environments.
    """
    def __init__(self, r_path, system_site_packages=False, recommended_packages=True, clear=False,
                 symlinks=False, upgrade=False, prompt=None):
        super().__init__(system_site_packages=system_site_packages, clear=clear,
                         symlinks=symlinks, upgrade=upgrade, prompt=prompt)
        del self.with_pip
        self.r_path = r_path
        if self.system_site_packages:
            self.base_packages = False
            self.recommended_packages = False
        else:
            self.base_packages = True
            self.recommended_packages = recommended_packages

    def create(self, env_dir):
        """
        Create a virtual environment in a directory.
        :param env_dir: The target directory to create an environment in.
        """
        env_dir = os.path.abspath(env_dir)
        context = self.ensure_directories(env_dir)
        # TODO-ROB: pip will eventually be beRi
        # See issue 24875. We need system_site_packages to be False
        # until after pip is installed.
        true_system_site_packages = self.system_site_packages
        self.system_site_packages = False
        context.config_dict = self.create_configuration(context)
        self.setup_r(context)
        # TODO-ROB: pip will eventually be beRi
        # if self.with_pip:
        #     self._setup_pip(context)
        if not self.upgrade:
            self.setup_scripts(context)
            # TODO-ROB: Setup .Rprofile using a default one included with the package
            # self.setup_r_profile(context)
            # TODO-ROB: Setup .Renviron using a default one included with the package
            # self.setup_r_environ(context)
            self.post_setup(context)
        if true_system_site_packages:
            # We had set it to False before, now
            # restore it and rewrite the configuration
            self.system_site_packages = True
            self.create_configuration(context)

    def ensure_directories(self, env_dir):
        """
        Create the directories for the environment.
        Returns a context object which holds paths in the environment,
        for use by subsequent logic.

        :param env_dir:
        :return:
        """

        def create_if_needed(d):
            if not os.path.exists(d):
                os.makedirs(d)
            elif os.path.islink(d) or os.path.isfile(d):
                raise ValueError('Unable to create directory %r' % d)

        if os.path.exists(env_dir) and self.clear:
            self.clear_directory(env_dir)
        user_config = os.path.join(env_dir, "renv.yaml")
        context = types.SimpleNamespace()
        context.user_config = user_config
        context.env_dir = env_dir
        context.env_name = os.path.split(env_dir)[1]
        prompt = self.prompt if self.prompt is not None else context.env_name
        context.prompt = '(%s) ' % prompt
        create_if_needed(env_dir)
        # TODO-ROB:  This may be tied in with a config file or with an outside environment variable.
        # System R files and paths
        r_exe = "R"
        r_script = "Rscript"
        context.R_exe = r_exe
        context.R_script = r_script
        context.R_version = os.path.split(self.r_path)[1]
        context.abs_R_exe = os.path.join(self.r_path, "bin", r_exe)
        context.abs_R_script = os.path.join(self.r_path, "bin", r_script)
        context.abs_R_path = self.r_path
        logging.info(f"System R(version):  {self.r_path}({context.R_version})")

        # TODO-config:  Set default r_home in YAML.  Create parameter for user setting.
        # TODO-config:  Add to .Renviron file.
        # R-Environment R files and paths
        if sys.platform == 'win32':
            r_env_home = env_dir
            r_abs_home = self.r_path
            r_env_include = r_abs_include = "include"
        else:
            r_env_home = os.path.join(env_dir, 'lib', "R")
            r_abs_home = os.path.join(self.r_path, 'lib', "R")
            r_env_include = os.path.join(r_env_home, "include")
            r_abs_include = os.path.join(self.r_path, "include")
        # Issue 21197: create lib64 as a symlink to lib on 64-bit non-OS X POSIX
        create_if_needed(r_env_home)
        if (sys.maxsize > 2**32) and (os.name == 'posix') and (sys.platform != 'darwin'):
            os.mkdir(os.path.join(env_dir, 'lib64'))
            link_path = os.path.join(env_dir, 'lib64', 'R')
            if not os.path.exists(link_path):   # Issue #21643
                os.symlink(r_env_home, link_path)
        binname = 'bin'
        r_env_libs = os.path.join(r_env_home, 'library')
        r_abs_libs = os.path.join(r_abs_home, 'library')
        context.bin_name = binname
        context.env_R_home = r_env_home
        context.abs_R_home = r_abs_home
        context.env_R_libs = r_env_libs
        context.abs_R_libs = r_abs_libs
        context.env_R_include = os.path.join(env_dir, r_env_include)
        context.env_bin_path = binpath = os.path.join(env_dir, binname)
        context.bin_path = binpath
        context.env_R_exe = os.path.join(binpath, r_exe)
        context.env_R_script = os.path.join(binpath, r_script)
        create_if_needed(context.env_R_libs)
        create_if_needed(context.env_R_include)
        create_if_needed(binpath)
        logging.info(f"Environment R:  {r_env_home}")
        return context

    def create_configuration(self, context):
        """
        Create a configuration file indicating where the environment's R
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
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8')as f:
                user_config = yaml.load(f)
        else:
            user_config = {}

        with open(path, 'w', encoding='utf-8') as f:
            if self.system_site_packages:
                sep = ";" if sys.platform == "win32" else ":"
                config_dict["R_LIBS_USER"] = "%s%s%s" % (context.env_R_libs, sep, context.abs_R_libs)
            else:
                config_dict["R_LIBS_USER"] = context.env_R_libs
                if self.recommended_packages:
                    Rcmd = f"{context.abs_R_script} " \
                           f"-e \'base::cat(rownames(installed.packages(priority=\"recommended\")))\'"
                    recommended_pkgs = subprocess.Popen([Rcmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                                        shell=True, encoding='utf-8')
                    error = recommended_pkgs.stderr.readlines()
                    out = recommended_pkgs.stdout.readlines()
                    recommended_pkgs.wait()
                    recommended_pkgs = out[0].split(" ")
                if self.base_packages:
                    Rcmd = f"{context.abs_R_script} " \
                           f"-e \'base::cat(rownames(installed.packages(priority=\"base\")))\'"
                    base_pkgs = subprocess.Popen([Rcmd], stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                                        shell=True, encoding='utf-8')
                    error = base_pkgs.stderr.readlines()
                    out = base_pkgs.stdout.readlines()
                    base_pkgs.wait()
                    base_pkgs = out[0].split(" ")
                pkgs = recommended_pkgs + base_pkgs
                # TODO-config: This may need to be separate for windows vs linux
                for pkg in pkgs:
                    abs_pkg_path = os.path.join(context.abs_R_libs, pkg)
                    env_pkg_path = os.path.join(context.env_R_libs, pkg)
                    copier(abs_pkg_path, env_pkg_path)
                    if not os.path.islink(env_pkg_path):
                        os.chmod(env_pkg_path, 0o755)

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

    def replace_variables(self, text, context):
        """
        Replace variable placeholders in script text with context-specific
        variables.
        Return the text passed in , but with variables replaced.
        :param text: The text in which to replace placeholder variables.
        :param context: The information for the environment creation request
                        being processed.
        """
        text = text.replace('__VENV_DIR__', context.env_dir)
        text = text.replace('__VENV_NAME__', context.env_name)
        text = text.replace('__VENV_PROMPT__', context.prompt)
        text = text.replace('__VENV_BIN_NAME__', context.bin_name)
        # NEW:
        text = text.replace('__VENV_R__', context.env_R_exe)
        text = text.replace('__VENV_RSCRIPT__', context.env_R_script)
        text = text.replace('__R_LIBS_USER__', context.config_dict["R_LIBS_USER"])
        text = text.replace('__R_VERSION__', context.config_dict["R_VERSION"])
        text = text.replace('__R_HOME__', context.config_dict["R_ENV_HOME"])
        text = text.replace('__R_INCLUDE_DIR__', context.config_dict["R_INCLUDE_DIR"])
        text = text.replace('__CRAN_MIRROR__', context.config_dict["CRAN_MIRROR"])
        text = text.replace('__CRANEXTRA_MIRROR__', context.config_dict["CRANEXTRA_MIRROR"])
        text = text.replace('__STANDARD_PKG_LIST__', context.config_dict["STANDARD_PKG_LIST"])
        text = text.replace('__REPRODUCIBLE_WORKFLOW_PKG_LIST__', context.config_dict["REPRODUCIBLE_WORKFLOW_PKG_LIST"])

        return text

    # TODO-ROB: Test if the scripts work properly with this build.
    # TODO-ROB: Different variables will need to be created in the replace_variables function.
    # TODO-ROB: The variables will have to be changed in the /scripts/* files.
    # def install_scripts(self, context, path):
    #     pass

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

    def format_pkg_list(self, config_dict):
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
