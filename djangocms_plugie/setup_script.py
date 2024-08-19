import os
import shutil
import sys
import argparse
from djangocms_plugie import __version__ as VERSION


def setup_project(project_dir: str) -> None:
    """"
    Setup the project in the specified directory. This function copies the 
    custom methods and the config file to the project directory.

    :param project_dir: str, the directory of the project to setup
    """
    project_dir = os.path.join(os.getcwd(), project_dir)

    if not os.path.exists(project_dir):
        print(f"Project directory '{project_dir}' does not exist.")
        sys.exit(1)

    plugie_dir = os.path.join(project_dir, "plugie")
    os.makedirs(plugie_dir, exist_ok=True)

    # TODO: Separate these functions into different commands
    copy_config_file(project_dir)
    copy_custom_methods(plugie_dir)
    copy_tests(project_dir)

    print(f"Setup completed successfully.")

def copy_custom_methods(plugie_dir: str) -> None:
    """"
    Copy the default custom methods to the plugie directory.

    :param plugie_dir: str, the directory of the plugie app
    """
    source_dir = os.path.join(
        os.path.dirname(__file__), "methods", "custom_methods")

    if not os.path.exists(source_dir):
        print(f"Static directory '{source_dir}' does not exist.")
        sys.exit(1)

    static_dest_dir = os.path.join(plugie_dir, "custom_methods")

    if os.path.exists(static_dest_dir):
        print(f"Static directory '{static_dest_dir}' already exists. \
              Please remove it first.")
        sys.exit(1)

    shutil.copytree(source_dir, static_dest_dir)
    print(f"Static files copied to '{static_dest_dir}' successfully.")

def copy_config_file(project_dir: str) -> None:
    """
    Copy the default config file to the project directory.

    :param project_dir: str, the directory of the project to setup
    """
    config_source = os.path.join(os.path.dirname(__file__), "static", "djangocms_plugie", "plugie_config.json")
    config_dest = os.path.join(project_dir, "plugie_config.json")

    shutil.copy(config_source, config_dest)
    print(f"Config file copied to '{config_dest}' successfully.")

def copy_tests(project_dir: str) -> None:
    """"
    Copy the tests to the plugie directory.

    :param project_dir: str, the directory of the project
    """
    source_dir = os.path.join(
        os.path.dirname(__file__), "tests")

    if not os.path.exists(source_dir):
        print(f"Static directory '{source_dir}' does not exist.")
        sys.exit(1)

    static_dest_dir = os.path.join(project_dir, "plugie_tests")

    if os.path.exists(static_dest_dir):
        print(f"Static directory '{static_dest_dir}' already exists. \
              Please remove it first.")
        sys.exit(1)

    shutil.copytree(source_dir, static_dest_dir)
    print(f"Tests copied to '{static_dest_dir}' successfully.")


def show_version() -> None:
    """ Show the current version of plugie."""
    print(f"plugie version {VERSION}")


def show_help() -> None:
    """ Show the help message for the setup script."""
    help_text = """
    Usage: plugie <command> [options]

    Commands:
        <project_dir>       Set up the project in the specified directory.
        version             Show the current version of plugie.
        help                Show this help message.
    """
    print(help_text)


def main() -> None:
    """
    Main function for the setup script. This function parses the command line
    arguments and calls the appropriate function.
    """

    parser = argparse.ArgumentParser(description='Setup djangocms_plugie project.')
    parser.add_argument(
        'project_dir',
        nargs='?',
        help='The directory of the project to setup'
    )
    parser.add_argument(
        '-v', '--version',
        action='store_true',
        help='Show the version of plugie'
    )

    args = parser.parse_args()

    if args.version:
        show_version()
    elif args.project_dir:
        setup_project(args.project_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
