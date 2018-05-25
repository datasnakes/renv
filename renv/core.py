from venv import EnvBuilder


class RenvBuilder(EnvBuilder):
    """
    The RenvBuilder class is a giant rework of the venv.EnvBuilder class.
    The EnvBuilder class can be found here:
    https://github.com/python/cpython/blob/3.6/Lib/venv/__init__.py

    This initial skeleton class includes all of the methods that will need
    to be reworked for R environments.
    """
    def __init__(self):
        pass

    def create(self, env_dir):
        pass

    def ensure_directories(self, env_dir):
        pass

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
