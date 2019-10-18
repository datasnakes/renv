[![PyPI version](https://badge.fury.io/py/renv.svg)](https://badge.fury.io/py/renv)
[![Build Status](https://travis-ci.com/datasnakes/renv.svg?branch=master)](https://travis-ci.com/datasnakes/renv)

# renv (beta)

Creating virtual environments for R. (currently a Linux-only implementation)
# hackseq19

For hackseq19 we intend to design a working implementation or prototype of renv for Windows 
and MacOS.  The current implementation only works for Linux.

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

Please submit an [issue](https://github.com/datasnakes/renv/issues)
or [PR](https://github.com/datasnakes/renv/pulls). We'd love to get
community feedback.

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

## Maintainers

Rob Gilmore | [@grabear](https://github.com/grabear) | [✉](mailto:robgilmore127@gmail.com)  
Santina Lin | [@santina](https://github.com/santina) | [✉](mailto:santina424@gmail.com)  
Shaurita Hutchins | [@sdhutchins](https://github.com/sdhutchins) | [✉](mailto:sdhutchins@outlook.com)
