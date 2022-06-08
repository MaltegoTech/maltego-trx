import os
import shutil
import sys

import maltego_trx

"""
Receive commands run to start a new project.
"""


def execute_from_command_line():
    args = sys.argv[1:]

    if args[0].lower() == "start":
        run_start(args[1:])
    elif args[0].lower() == "init":
        run_start([], create_dir=False)
    else:
        print("Command not recognised. Available commands are: \n 'start <project_name>' \n 'init'")


def run_start(args, create_dir: bool = True):
    if create_dir:
        project = args[0]
        project_dir = os.path.join(os.getcwd(), project)
        os.makedirs(project_dir)
    else:
        project_dir = os.getcwd()
        project = os.path.basename(project_dir)

    try:
        template_dir_path = os.path.join(maltego_trx.__path__[0], "template_dir")
        copytree(template_dir_path, project_dir)
        print("Successfully created a new project in the '%s' folder." % project)
    except FileExistsError:
        print("ERROR: '%s' already exists" % project_dir)
    except OSError as e:
        print("ERROR: %s" % str(e))


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        if "__pycache__" not in item and ".pyc" not in item:
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
