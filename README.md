# renv (beta)

Creating virtual environments for R. (currently a Linux-only implementation)

## Description

One of the problems with using R for data analysis can be dependency issues especially for
scientists who use multiple versions of R or R packages and have a large number of
projects that they are developing with R. Dependency issues are especially prevalent among those individuals or groups
that are developing R packages.  `renv` is a [Python style](https://github.com/python/cpython/blob/3.6/Lib/venv/__init__.py)
virtual environment manager for creating virtual environments for R.

## Installation

This package is being managed with [`poetry`](https://github.com/sdispater/poetry).

```bash
# Clone the repository
git clone https://github.com/datasnakes/renv.git

cd renv

# Make sure you have activated an environment of Python >= 3.6

# Get poetry and build the project using it
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

poetry install

poetry build

pip install dist/renv-0.2.0-py2.py3-none-any.whl
```

## Usage

Renv is currently in beta and is only supported in Linux so there may be some issues if your R has been
installed in a way other than the default. There are probably plenty of
unforeseen bugs, misspellings, and general use cases where the code could be
more efficient. Please submit an [issue](https://github.com/datasnakes/renv/issues)
or [PR](https://github.com/datasnakes/renv/pulls). We'd love to get
community feedback.

The default .Rprofile also prompts you to install some commonly used
packages. The functionality of this is useful, but will change for the
actual release of this package.

### Commands

Once you have renv installed, you can create an R environment by a simple command:

```bash
renv -n myenv
```

An environment folder `myenv` will be created under `$HOME/.renv`.

To activate the environment 
```
cd $HOME\.renv\myenv\bin
. ./activate 
```

To deactivate the R environment:

```bash
deactivate
```


Use `--help` to see the other command-line options.

```console
user@host:~$ renv --help
Usage: renv [OPTIONS]

Options:
  -r, --r_home TEXT               Provide the root of the directory tree where
                                  R is installed.  This would be R's
                                  installation directory when using
                                  ./configure --prefix=<r_home>.
  -n, --env_name TEXT             Name of the environment.
  -d, --env_home TEXT              A directory for creating the environment in.
  -b, --binpath TEXT              Provide the bin directory if R was installed
                                  when using ./configure --bindir=<binpath>.
  -l, --libpath TEXT              Provide the lib directory if R was installed
                                  when using ./configure --libdir=<libpath>.
  -i, --includepath TEXT          Provide the include directory if R was
                                  installed when using ./configure
                                  --includedir=<includepath>.
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
  -v, --verbose                   Show verbose cli output.
  -V, --version                   Show the version of renv and exit.
  --help                          Show this message and exit.
```


### Creating an R Environment

```console
user@host:~$ renv -r /usr/local/R -d ~/projects/rna-brain
user@host:~$ source projects/rna-brain/bin/activate
(rna-brain) user@host:~$ R

R version x.y.z (YYY-MM-DD) -- "Dist"
Copyright (C) YYY The R Foundation for Statistical Computing
Platform: Renv is working for some linux distrubutions

R is free software and comes with ABSOLUTELY NO WARRANTY.
You are welcome to redistribute it under certain conditions.
Type 'license()' or 'licence()' for distribution details.

R is a collaborative project with many contributors.
Type 'contributors()' for more information and
'citation()' on how to cite R or R packages in publications.

Type 'demo()' for some demos, 'help()' for on-line help, or
'help.start()' for an HTML browser interface to help.
Type 'q()' to quit R.


..................Attempting to Load Bioconductor...................

Warning: Prompting for Bioconductor Installation...

Do you want to install Bioconductor??? [Y/N]
n

..................Attempting to Load Devtools...................

Warning: Prompting for Devtools Installation...

Do you want to install Devtools??? [Y/N]
n

..................Attempting to Load Tidyverse...................

Warning: Prompting for Tidyverse Installation...

Do you want to install Tidyverse??? [Y/N]
n
Warning messages:
1: In library(package, lib.loc = lib.loc, character.only = TRUE, logical.return = TRUE,  :
  there is no package called ‘BiocInstaller’
2: In library(package, lib.loc = lib.loc, character.only = TRUE, logical.return = TRUE,  :
  there is no package called ‘devtools’
3: In library(package, lib.loc = lib.loc, character.only = TRUE, logical.return = TRUE,  :
  there is no package called ‘tidyverse’
>

```
## Features

1.  Creates a default R virtual environment using default config settings
    or a YAML file in the pre-existing environment directory.
2.  Manages the user's and the environment's .Rprofile and .Renviron
    files.

Below is an example of the YAML config file (there may be mistakes or
missing keys). Try to use absolute paths.

```yaml
R_ABS_HOME: "/home/grabear/R-installs/R-3.4.3/lib64/R"
R_ENV_HOME: "/home/grabear/rna-brain"
R_LIBS_USER: "/home/grabear/rna-brain/lib64/R/library"
R_INCLUDE_DIR: "/home/grabear/rna-brain/lib64/R/include"
R_VERSION: "3.4.3"

# LIST OF DEFAULT variables for .Rprofile
CRAN_MIRROR: "https://cran.rstudio.com/"
CRANEXTRA_MIRROR: "https://mirrors.nics.utk.edu/cran/"

# Determine how to format this for .Rprofile
STANDARD_PKG_LIST:
  BiocInstaller: "Bioconductor"
  devtools: "Devtools"
  tidyverse: "Tidyverse"

REPRODUCIBLE_WORKFLOW_PKG_LIST:
  packrat: "Packrat"
  miniCRAN: "MiniCRAN"
```

## Questions

### Why renv?

Tools for creating reproducible workflows with R have been needed for a
long time. Renv gets its inspiration from
[packrat](https://rstudio.github.io/packrat/), which allows you to
create isolated package libraries, and python's
[venv](https://docs.python.org/3/library/venv.html) module, which
creates an environment with its own package library **AND** python
binaries. Renv, therefore, helps user better manage a system with
multiple installations of R by creating a virtual environments for
specific versions of R that have their own R binaries (R and Rscript) as
well as their own isolated package libraries.

### Why click and poetry?

Click is used over argparse for speed of development. It requires an
extra dependency, but it's easy to use and what we know. Poetry is used
for similar reasons. It's a developing project, so we may have regrets
later down the road, but for now it's proven to be a very useful tool.

### Why not develop everything in R?

Again, we are going with what we know. We aren't unfamiliar with
programming or making packages with R, but we are way better at
developing and maintaining python code. Virtual environments are already
widely used for the python language, which means we don't have to
recreate the _.whl_.

## Maintainers

Rob Gilmore | [@grabear](https://github.com/grabear) | [✉](mailto:robgilmore127@gmail.com)  
Santina Lin | [@santina](https://github.com/santina) | [✉](mailto:santina424@gmail.com)  
Shaurita Hutchins | [@sdhutchins](https://github.com/sdhutchins) | [✉](mailto:sdhutchins@outlook.com)
