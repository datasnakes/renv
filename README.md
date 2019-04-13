[![PyPI version](https://badge.fury.io/py/renv.svg)](https://badge.fury.io/py/renv)
[![Build Status](https://travis-ci.com/datasnakes/renv.svg?branch=master)](https://travis-ci.com/datasnakes/renv)

# renv (beta)

Creating virtual environments for R. (currently a Linux-only implementation)

## Description

One of the problems with using R for data analysis can be dependency issues especially for
scientists who use multiple versions of R or R packages and have a large number of
projects that they are developing with R. Dependency issues are especially prevalent among those individuals or groups
that are developing R packages.  `renv` is a [Python style](https://github.com/python/cpython/blob/3.6/Lib/venv/__init__.py)
virtual environment manager for creating virtual environments for R.

## Installation

This package is being managed with [`poetry`](https://github.com/sdispater/poetry) and is also available on PyPi.

```bash
pip install renv
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

Once you have renv installed, you need to initialize renv to set up the `.beRi/.renv` folder in your `$HOME` directory:

```bash
renv init
```

Now, you can easily create an environment:

```bash
renv -e myenv -r /path/to/R/folder # Find your current R folder is using `which R` on Linux.
```

An environment folder named `myenv` will be created in `$HOME/.beRi/.renv`.

To activate the environment:
```
cd $HOME/.beRi/.renv/myenv/bin
. ./activate 
```

To deactivate the R environment:

```bash
deactivate
```


Use `--help` to see the other command-line options.

```console
user@host:~$ renv --help
Usage: renv [OPTIONS] COMMAND [ARGS]...

Options:
  -r, --r_home TEXT               Provide the root of the directory tree where
                                  R is installed ($R_HOME).  This would be R's
                                  installation directory when using
                                  ./configure --prefix=<r_home>.  [required]
  -e, --env_name TEXT             Name of the environment.  [required]
  -p, --path TEXT                 An absolute installation path for renv.
                                  [default: ~/.beRi]
  -n, --name TEXT                 A directory name for renv.  [default: .renv]
  -b, --bindir TEXT               Provide the bin directory if R was installed
                                  when using ./configure --bindir=<binpath>.
  -l, --libdir TEXT               Provide the lib directory if R was installed
                                  when using ./configure --libdir=<libpath>.
  -i, --includedir TEXT           Provide the include directory if R was
                                  installed when using ./configure
                                  --includedir=<includepath>.
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
  --help                          Show this message and exit.

Commands:
  init  Initialize renv using the <path>/<name>.
                         Show this message and exit.
```


### Creating an R Environment

```console
user@host:~$ renv  -e ~/projects/rna-brain -r /usr/local/apps/R/R-3.4.4/
user@host:~$ source ~/projects/rna-brain/bin/activate
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

## Questions ???

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
