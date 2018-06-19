# renv

Creating virtual environments for R with Python's venv module.

## Installation

This package is being managed with [`poetry`](https://github.com/sdispater/poetry).

```
# Clone the repository
git clone https://github.com/datasnakes/renv.git

cd renv

poetry build

pip install dist/renv-0.2.0-py2.py3-non-any.whl
```

## Usage

```
$ renv --help
Usage: renv [OPTIONS]

Options:
  -r, --r_path TEXT               Provide the root of the directory tree where
                                  R is installed.  This would be R's
                                  installation directory when using
                                  ./configure --prefix=<r_path>.
  -sp, --system_site_packages BOOLEAN
                                  This determines whether or not the
                                  R_LIBS_USER environment variable utilizes
                                  the original R's package library as a
                                  secondary source for loading packages.
  -rp, --recommended_packages BOOLEAN
                                  This determines wheather or not the
                                  recommended packages are installed in theR
                                  environment along with the base packages.
                                  In most cases it's best to keep thedefault
                                  value.
  --clear BOOLEAN                 Deletes the contents of the environment
                                  directory if it already exists, before
                                  environment creation.
  -u, --upgrade BOOLEAN           Upgrades the environment directory to use
                                  this version of R.
  -p, --prompt TEXT               Provide an alternative prompt prefix for
                                  this environment.
  -d, --env_dir TEXT              A directory for creating the environment in.
  --help                          Show this message and exit.
```

## Features

## Why renv?

### Strategy

Use python's [venv module API](https://docs.python.org/3/library/venv.html#api)
in order to create R virtual environments.  This can be done using the EnvBuilder class,
while supressing the setup_python() method.

## Maintainers

Rob Gilmore | [@grabear](https://github.com/grabear) | [✉](mailto:robgilmore127@gmail.com)
Shaurita Hutchins | [@sdhutchins](https://github.com/sdhutchins) | [✉](mailto:sdhutchins@outlook.com)