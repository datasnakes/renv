# renv
Creating virtual environments for R with Python's venv module.

## Strategy

Use python's [venv module API](https://docs.python.org/3/library/venv.html#api) in order to create R virtual environments.  This can be done using the EnvBuilder class, while supressing the setup_python() method.
