from venv import EnvBuilder
import logging
import os
import shutil
import subprocess
import sys
import types


class RenvBuilder(EnvBuilder):
    """
    The RenvBuilder class is a giant rework of the venv.EnvBuilder class.
    The EnvBuilder class can be found here:
    https://github.com/python/cpython/blob/3.6/Lib/venv/__init__.py

    This initial skeleton class includes all of the methods that will need
    to be reworked for R environments.
    """
    def __init__(self, r_path, system_site_packages=False, clear=False,
                 symlinks=False, upgrade=False, prompt=None):
        super().__init__(system_site_packages=system_site_packages, clear=clear,
                         symlinks=symlinks, upgrade=upgrade, prompt=prompt)
        del self.with_pip
        self.r_path = r_path

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
        self.create_configuration(context)
        self.setup_r(context)
        # TODO-ROB: pip will eventually be beRi
        # if self.with_pip:
        #     self._setup_pip(context)
        if not self.upgrade:
            self.setup_scripts(context)
            # TODO-ROB: Setup .Rprofile using a default one included with the package
            # TODO-ROB: Setup .Renviron using a default one included with the package
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

        context = types.SimpleNamespace()
        context.env_dir = env_dir
        context.env_name = os.path.split(env_dir)[1]
        prompt = self.prompt if self.prompt is not None else context.env_name
        context.prompt = '(%s) ' % prompt
        create_if_needed(env_dir)
        # TODO-ROB:  This may be tied in with a config file or with an outside environment variable.
        # System R files and paths
        r_exe = "R.exe"
        r_script = "Rscript"
        context.R_abs_exe = os.path.join(self.r_path, r_exe)
        context.R_abs_script = os.path.join(self.r_path, r_script)
        context.R_exe = r_exe
        context.R_script = r_script
        context.R_path = self.r_path

        # TODO-config:  Set default r_home in YAML.  Create parameter for user setting.
        # TODO-config:  Add to .Renviron file.
        # R-Environment R files and paths
        if sys.platform == 'win32':
            r_home = env_dir
            r_include_dir = "include"
        else:
            r_home = os.path.join(env_dir, 'lib', "R")
            r_include_dir = os.path.join(r_home, "include")
        # Issue 21197: create lib64 as a symlink to lib on 64-bit non-OS X POSIX
        if (sys.maxsize > 2**32) and (os.name == 'posix') and (sys.platform != 'darwin'):
            link_path = os.path.join(env_dir, 'lib64', 'R')
            if not os.path.exists(link_path):   # Issue #21643
                os.symlink(r_home, link_path)
        binname = 'bin'
        context.bin_name = binname
        context.inc_path = os.path.join(env_dir, r_include_dir)
        context.bin_path = binpath = os.path.join(env_dir, binname)
        context.env_R_exe = os.path.join(binpath, r_exe)
        context.env_R_script = os.path.join(binpath, r_script)
        create_if_needed(r_include_dir)
        create_if_needed(r_home)
        create_if_needed(binpath)
        return context

    def create_configuration(self, context):
        """
        Create a configuration file indicating where the environment's R
        was copied from, and whether the system site-packages should be made
        available in the environment.
        :param context: The information for the environment creation request
                        being processed.
        """
        # TODO-ROB: Work YAML configuration into this section
        context.cfg_path = path = os.path.join(context.env_dir, 'FAKE_Rcfg.yaml')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('R_HOME? = %s\n' % context.R_exe_dir)
            if self.system_site_packages:
                incl = 'true'
            else:
                incl = 'false'
            f.write('include-system-site-packages = %s\n' % incl)
            f.write('version = %d.%d.%d\n' % (3, 4, 3))
        # TODO-ROB:  This would only be apply under Windows.  This is called in setup_python(r)
        # if os.name == 'nt':
        #     def include_binary(self, f):
        #         if f.endswith(('.pyd', '.dll')):
        #             result = True
        #         else:
        #             result = f.startswith('python') and f.endswith('.exe')
        #         return result

    def setup_r(self, context):
        """
       Set up a R executable in the environment.
       :param context: The information for the environment creation request
                       being processed.
       """
        binpath = context.bin_path
        path = context.env_R_exe
        copier = self.symlink_or_copy
        copier(context.R_abs_exe, path)
        dirname = context.R_exe_dir
        if os.name != 'nt':
            if not os.path.islink(path):
                os.chmod(path, 0o755)
            # for suffix in ('python', 'python3'):
            for suffix in ('R', 'Rscript'):
                path = os.path.join(binpath, suffix)
                if not os.path.exists(path):
                    # Issue 18807: make copies if
                    # symlinks are not wanted
                    copier(context.env_exe, path, relative_symlinks_ok=True)
                    if not os.path.islink(path):
                        os.chmod(path, 0o755)
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
        text = text.replace('__VENV_R_NAME__', context.env_R_exe)
        text = text.replace('__VENV_RSCRIPT_NAME', context.env_R_script)
        return text

    # TODO-ROB: Test if the scripts work properly with this build.
    # TODO-ROB: Different variables will need to be created in the replace_variables function.
    # TODO-ROB: The variables will have to be changed in the /scripts/* files.
    # def install_scripts(self, context, path):
    #     pass

    def install_r(self):
        # New: install specified version of R in the R environment.
        pass

    def setup_r_profile(self):
        # New
        pass

    def setup_r_environ(self):
        # New
        pass
