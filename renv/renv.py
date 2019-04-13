import click
from renv import BaseRenvBuilder, get_system_venv


@click.group(invoke_without_command=True)
@click.option('--r_home', '-r', default=None,
              help="Provide the root of the directory tree where R is installed ($R_HOME).  This would be R's "
                   "installation directory when using ./configure --prefix=<r_home>.")
@click.option('--env_name', '-e', default=None,
              help="Name of the environment.")
@click.option("--path", "-p", default="~/.beRi",
              help="An absolute installation path for renv.", show_default=True)
@click.option("--name", "-n", default=".renv",
              help="A directory name for renv.", show_default=True)
@click.option('--bindir', '-b', default=None,
              help="Provide the bin directory if R was installed when using ./configure --bindir=<binpath>.")
@click.option('--libdir', '-l', default=None,
              help="Provide the lib directory if R was installed when using ./configure --libdir=<libpath>.")
@click.option('--includedir', '-i', default=None,
              help="Provide the include directory if R was installed when using ./configure --includedir=<includepath>.")
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
@click.option('--verbose', '-v', is_flag=True, default=False,
              help="Show verbose cli output.")
@click.pass_context
def renv(ctx, r_home, env_name, path, name, bindir, libdir, includedir, recommended_packages, clear,
         upgrade, prompt, verbose):
    ctx.ensure_object(dict)
    ctx.obj['path'] = path
    ctx.obj['name'] = name
    ctx.obj['env_name'] = env_name
    ctx.obj['r_home'] = r_home
    if path != "~/.beRi":
        raise NotImplementedError("Renv only supports installing into the home directory at this time.")

    if env_name and r_home:
        venvR = get_system_venv()
        ctx.obj['venvR'] = venvR
        builder = venvR(env_name=env_name, path=path, name=name, r_home=r_home, recommended_packages=recommended_packages,
              clear=clear, upgrade=upgrade, prompt=prompt, verbose=verbose, bindir=bindir, libdir=libdir,
              rincludedir=includedir)
        env_bin = builder.build_venv()
        click.secho("To activate: source " + env_bin + "/activate", fg="green")


@renv.command(help="Initialize renv using the <path>/<name>.")
@click.pass_context
def init(ctx):
    # Initialize renv
    BaseRenvBuilder(path=ctx.obj['path'], name=ctx.obj['name'], init=True)
