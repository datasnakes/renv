import click
from renv.core import RenvBuilder
import os
from pkg_resources import get_distribution


@click.command()
@click.option('--r_home', '-r', default=None,
              help="Provide the root of the directory tree where R is installed (%R_HOME).  This would be R's "
                   "installation directory when using ./configure --prefix=<r_home>.")
@click.option('--env_name', '-n', default=None,
              help="Name of the environment.")
@click.option('--env_home', '-d', default=None,
              help="A directory for creating the environment in.")
@click.option('--bindir', '-b',
              help="Provide the bin directory if R was installed when using ./configure --bindir=<binpath>.")
@click.option('--libdir', '-l',
              help="Provide the lib directory if R was installed when using ./configure --libdir=<libpath>.")
@click.option('--includepath', '-i',
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
def renv(r_home, env_name, env_home, bindir, libdir,
         includepath, system_site_packages,
         recommended_packages, clear, upgrade, prompt, verbose, version):
    # Print the version of renv
    if version:
        version = get_distribution('renv').version
        click.echo("renv version {}".format(version))
    else:
        if os.name == 'nt':
            use_symlinks = False
        else:
            use_symlinks = True

    builder = RenvBuilder(r_home=r_home, bindir_path=bindir, libdir=libdir, r_include_path=includepath,
                          system_site_packages=system_site_packages,
                          recommended_packages=recommended_packages,
                          clear=clear, symlinks=use_symlinks, upgrade=upgrade,
                          prompt=prompt, verbose=verbose)

    builder.create(env_home, env_name)
