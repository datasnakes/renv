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
        # TODO-ROB: Create a function for finding the R executable
        # TODO-ROB:  This may be tied in with a config file or with an outside environment variable.
        # env = os.environ
        # if sys.platform == 'darwin' and '__PYVENV_LAUNCHER__' in env:
        #     executable = os.environ['__PYVENV_LAUNCHER__']
        # else:
        #     executable = sys.executable


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
