import click
from renv.core import RenvBuilder
import os


@click.command()
@click.option('--r_path', '-r',
              help="Provide the root of the directory tree where R is installed.  This would be R's installation "
                   "directory when using ./configure --prefix=<r_path>.")
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
@click.option('--env_dir', '-d',
              help="A directory for creating the environment in.")
def renv(r_path, system_site_packages, recommended_packages, clear, upgrade, prompt, env_dir):
    if not os.path.exists(r_path):
        raise NotADirectoryError("%s is an")
    if os.name == 'nt':
        use_symlinks = False
    else:
        use_symlinks = True
    builder = RenvBuilder(r_path=r_path, system_site_packages=system_site_packages,
                          recommended_packages=recommended_packages, clear=clear, symlinks=use_symlinks,
                          upgrade=upgrade, prompt=prompt)
    builder.create(env_dir)
