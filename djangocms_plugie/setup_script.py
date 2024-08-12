import os
import shutil
import sys
import argparse

VERSION = '0.1.0'


def setup_project(project_dir):
    project_dir = os.path.join(os.getcwd(), project_dir)

    if not os.path.exists(project_dir):
        print(f"Project directory '{project_dir}' does not exist.")
        sys.exit(1)

    plugie_dir = os.path.join(project_dir, "plugie")
    os.makedirs(plugie_dir, exist_ok=True)

    copy_config_file(project_dir)
    copy_custom_methods(plugie_dir)

    print(f"Setup completed successfully.")

def copy_custom_methods(plugie_dir):
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

def copy_config_file(project_dir):
    config_source = os.path.join(os.path.dirname(__file__), "static", "djangocms_plugie", "plugie_config.json")
    config_dest = os.path.join(project_dir, "plugie_config.json")

    shutil.copy(config_source, config_dest)
    print(f"Config file copied to '{config_dest}' successfully.")


def show_version():
    print(f"plugie version {VERSION}")


def show_help():
    help_text = """
    Usage: plugie <command> [options]

    Commands:
        <project_dir>       Set up the project in the specified directory.
        version             Show the current version of plugie.
        help                Show this help message.
    """
    print(help_text)


def main():
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
