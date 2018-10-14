import subprocess
import os
import renv.utils as utils

def activate_environment(name, path=None):
    """
    Activate environment by calling activate_env.sh in the environment folder.
    :param name: name of the environment
    :param path: path of the environment
    :return: None
    """

    beri_env_path = ""

    # Build the environment path if it's not given.
    if path is None:
        # for linux:
        beri_env_path = os.path.join(utils.get_beri_path(), name)

    # Use the given R path if it's given.
    else:
        if not os.path.exists(path):
            raise Exception("The given R path does not exist.")

        beri_env_path = os.path.join(path, name)

    # Finally, check if the environment is already created.
    if not os.path.exists(beri_env_path):
        raise Exception("The environment " + name + " does not seem to exist because this path '" +
                        beri_env_path + "' does not exist.")

    # Activate the environment using the activate_env.sh
    activate_script_path = os.path.join(beri_env_path, "activate_beRi_env")
    subprocess.run(["source", activate_script_path, beri_env_path, name], shell=True)
