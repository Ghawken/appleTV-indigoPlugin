# python3
# auto_installer.py

import subprocess
from pathlib import Path
import sys
import indigo

def install_package_and_retry_import():
    current_directory = Path.cwd()  # Current directory
    parent_directory = current_directory.parent  # Parent directory
    pip_executable = "/Library/Frameworks/Python.framework/Versions/3.11/bin/pip3.11"
    requirements_file = current_directory / "requirements.txt"
    install_dir = parent_directory / "Packages"
    installation_output = f"Installing dependencies to '{install_dir}' based on '{requirements_file}'\n"
    # Execute the pip install command
    indigo.server.log(f"Installing Dependencies, one-time only, may time a minute or 2.  Please wait.")
    indigo.server.log(f"{installation_output}")
    try:
        result = subprocess.run([
            pip_executable, 'install', '-r', str(requirements_file), '-t', str(install_dir), '--disable-pip-version-check'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        # Save the output to a variable for later use
        installation_output += result.stdout
        # Check if installation was successful
        if result.returncode != 0:
            print(installation_output)
            print("An error occurred while installing packages.")
            sys.exit(1)
        return installation_output
    except FileNotFoundError as e:
        error_message = f"File not found error: {e}"
        print(error_message)
        sys.exit(1)
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        sys.exit(1)