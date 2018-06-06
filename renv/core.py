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
    def __init__(self, system_site_packages=False, clear=False,
                 symlinks=False, upgrade=False, prompt=None):
        super().__init__(system_site_packages=system_site_packages, clear=clear,
                         symlinks=symlinks, upgrade=upgrade, prompt=prompt)
        del self.with_pip

    def create(self, env_dir):
        """
        Create a virtual environment in a directory.
        :param env_dir: The target directory to create an environment in.
        """
        env_dir = os.path.abspath(env_dir)
        context = self.ensure_directories(env_dir)

    def ensure_directories(self, env_dir):
        """

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
        r_exe = "FAKE EXECUTABLE//PATH//R.exe"
        context.R_abs_exe = r_exe
        r_script = "FAKE EXECUTABLE//PATH//Rscript"
        context.R_abs_script = r_script
        # TODO-ROB: Create a function for finding the R executable
        # TODO-ROB:  This may be tied in with a config file or with an outside environment variable.
        # env = os.environ
        # if sys.platform == 'darwin' and '__PYVENV_LAUNCHER__' in env:
        #     executable = os.environ['__PYVENV_LAUNCHER__']
        # else:
        #     executable = sys.executable
        r_exe_dir, r_exe = os.path.split(os.path.abspath(r_exe))
        r_script_dir, r_script = os.path.split(os.path.abspath(r_script))
        context.R_exe_dir = r_exe_dir
        context.R_script_dir = r_script_dir
        context.R_exe = r_exe
        context.R_script = r_script

        # TODO-ROB: Get the package directory information from R
        # TODO-ROB: This can be relative, because the script just needs the naming convention per os
        binname = "FAKE_bin"
        incpath = "FAKE_include"
        libpath = os.path.join(env_dir, 'FAKE_R', "FAKE_platform", "FAKE_R_X.X.X")
        # if sys.platform == 'win32':
        #     binname = 'Scripts'
        #     incpath = 'Include'
        #     libpath = os.path.join(env_dir, 'Lib', 'site-packages')
        # else:
        #     binname = 'bin'
        #     incpath = 'include'
        #     libpath = os.path.join(env_dir, 'lib',
        #                            'python%d.%d' % sys.version_info[:2],
        #                            'site-packages')

        context.inc_path = path = os.path.join(env_dir, incpath)
        create_if_needed(path)
        create_if_needed(libpath)
        # TODO-ROB: Do we need this somehow?
        # Issue 21197: create lib64 as a symlink to lib on 64-bit non-OS X POSIX
        # if ((sys.maxsize > 2**32) and (os.name == 'posix') and
        #     (sys.platform != 'darwin')):
        #     link_path = os.path.join(env_dir, 'lib64')
        #     if not os.path.exists(link_path):   # Issue #21643
        #         os.symlink('lib', link_path)
        context.bin_path = binpath = os.path.join(env_dir, binname)
        context.bin_name = binname
        context.env_R_exe = os.path.join(binpath, r_exe)
        context.env_R_script = os.path.join(binpath, r_script)
        create_if_needed(binpath)
        return context

    def create_configuration(self, context):
        pass

    def setup_r(self):
        # This will be modeled after setup_python()
        pass

    def install_r(self):
        # New: install specified version of R in the R environment.
        pass

    def replace_variables(self, text, context):
        pass

    def install_scripts(self, context, path):
        pass

    def post_setup(self, context):
        pass

    def setup_r_profile(self):
        # New
        pass

    def setup_r_environ(self):
        # New
        pass
