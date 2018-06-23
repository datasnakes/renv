# renv (beta)

Creating virtual environments for R.

## Installation

This package is being managed with [`poetry`](https://github.com/sdispater/poetry).

```
# Clone the repository
git clone https://github.com/datasnakes/renv.git

cd renv

poetry build

pip install dist/renv-0.2.0-py2.py3-non-any.whl
```

## Why renv?

Tools for creating reproducible workflows with R have been needed for a
long time. Renv gets it's inspiration from
[packrat](https://rstudio.github.io/packrat/), which allows you to
create isolated package libraries, and python's
[venv](https://docs.python.org/3/library/venv.html) module, which
creates an environment with it's own package library **AND** python
binaries. Renv, therefore, helps user better manage a system with
multiple installations of R by creating a virtual environments for
specific versions of R that have their own R binaries (R and Rscript) as
well as their own isolated package libraries.

## Usage

Renv is currently in beta so there may be some issues if your R has been
installed in a way other than the default. There are probably plenty of
unforeseen bugs, misspellings, and general cases where the code could be
more efficient. Please submit an [issue](https://github.com/datasnakes/renv/issues)
or [PR](https://github.com/datasnakes/renv/pulls). We'd love to get
community feedback.

The default .Rprofile also prompts you to install some commonly used
packages. The functionality of this is useful, but will change for the
actual release of this package.

```bash
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

```bash
grabear@host:~$ renv -r /usr/local/R -d ~/projects/rna-brain
grabear@host:~$ source projects/rna-brain/bin/activate
(rna-brain) grabear@host:~$ R

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
2.  Manages users and the environments .Rprofile and .Renviron files
    during the usage of an R environment.

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

## Maintainers

Rob Gilmore | [@grabear](https://github.com/grabear) | [✉](mailto:robgilmore127@gmail.com)
Shaurita Hutchins | [@sdhutchins](https://github.com/sdhutchins) | [✉](mailto:sdhutchins@outlook.com)