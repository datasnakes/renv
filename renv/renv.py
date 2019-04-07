import click
from renv import BaseRenvBuilder, get_system_venv
import os
from pkg_resources import get_distribution


@click.group()
@click.option('--r_home', '-r', default=None,
              help="Provide the root of the directory tree where R is installed ($R_HOME).  This would be R's "
                   "installation directory when using ./configure --prefix=<r_home>.")
@click.option('--env_name', '-n', default=None,
              help="Name of the environment.")
@click.option('--env_home', '-d', default=None,
              help="A directory for creating the environment in.")
@click.option("--path", "-p", default="~/.beRi",
              help="An absolute installation path for renv.", show_default=True)
@click.option("--name", "-n", default=".renv",
              help="A directory name for renv.", show_default=True)
@click.option('--bindir', '-b',
              help="Provide the bin directory if R was installed when using ./configure --bindir=<binpath>.")
@click.option('--libdir', '-l',
              help="Provide the lib directory if R was installed when using ./configure --libdir=<libpath>.")
@click.option('--includedir', '-i',
              help="Provide the include directory if R was installed when using ./configure --includedir=<includepath>.")
@click.option('--system_site_packages', '-sp', type=bool, default=False,
              help="This determines whether or not the R_LIBS_USER environment variable utilizes the "
                   "original R's package library as a secondary source for loading packages.")
@click.option('--recommended_packages', '-rp', type=bool, default=True,
              help="This determines wheather or not the recommended packages are installed in the"
                   "R environment along with the base packages.  In most cases it's best to keep the"
                   "default value.")
@click.option('--clear', type=bool, default=False,
              help="Deletes the contents of the environment directory if it already exists, "
                   "before environment creation.")
@click.option('--upgrade', '-u', type=bool, default=False,
              help="Upgrades the environment directory to use this version of R.")
@click.option('--prompt', '-p', default=None,
              help="Provide an alternative prompt prefix for this environment.")
@click.option('--verbose', '-v', is_flag=True,
              help="Show verbose cli output.")
@click.option('--version', '-V', is_flag=True,
              help="Show the version of renv and exit.")
@click.pass_context
def renv(ctx, r_home, env_name, env_home, path, name, bindir, libdir, includedir, system_site_packages, recommended_packages, clear,
         upgrade, prompt, verbose, version):
    ctx.ensure_object(dict)
    ctx.obj['path'] = path
    ctx.obj['name'] = name
    if path != "~/.beRi":
        raise NotImplementedError("Renv only supports installing into the home directory at this time.")

    venvR = get_system_venv()
    ctx.obj['venvR'] = venvR


@renv.command(help="Initialize renv using the <path>/<name>.")
@click.pass_context
def init(ctx):
    # Initialize renv
    BaseRenvBuilder(path=ctx.obj['path'], name=ctx.obj['name'], init=True)