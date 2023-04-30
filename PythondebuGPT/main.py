import os
import subprocess
import sys
import argparse
import shutil
from pathlib import Path
import concurrent.futures 

import openai 

# Ensure API key is set
if not openai.api_key:
    print("Error: The OPENAI_API_KEY environment variable is not set.")
    sys.exit(1) 

openai.api_key = os.environ.get("OPENAI_API_KEY") 

# Import additional modules for the new features
import logging
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
import difflib
import time
import itertools
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict 

# Set up the logging system
logging.basicConfig(filename="autodebug.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s") 

# Progress indicator
def progress_spinner():
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    while True:
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b') 

# Dependency management
def check_dependencies(dependencies):
    missing_dependencies = []
    for dependency in dependencies:
        try:
            pkg_resources.require(dependency)
        except (DistributionNotFound, VersionConflict):
            missing_dependencies.append(dependency)
    return missing_dependencies 

def install_dependencies(dependencies):
    for dependency in dependencies:
        subprocess.run([sys.executable, "-m", "pip", "install", dependency]) 

# Rest of the functions remain unchanged 

def run_python_file(filename):
    try:
        output = subprocess.check_output(["python3", filename])
        return True, output
    except subprocess.CalledProcessError as e:
        return False, e.output 

def fix_python_code(code, error_output):
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=(
            f"I am an AI trained to debug Python code. "
            f"Here is a Python script with an error message as it showed up in the Terminal:\n\n---Code Start---\n{code}\n---Code End---\n\n"
            f"---Error Output Start---\n{error_output}\n---Error Output End---\n\n"
            "Please provide only the complete fixed Python code without any additional text or explanations."
        ),
        max_tokens=1024,
        n=1,
        stop=["---Code End---"],
        temperature=0.5,
        top_p=0.95,  # Narrow the token selection and improve code quality.
    )
    return response.choices[0].text.strip() 

def backup_file(target_file):
    backup_file_path = target_file + ".bak"
    shutil.copy2(target_file, backup_file_path)
    return backup_file_path 

def compare_files(file1, file2):
    with open(file1, "r") as f1, open(file2, "r") as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines() 

    diff = difflib.unified_diff(lines1, lines2, fromfile=file1, tofile=file2) 

    return "\n".join(diff) 

def auto_debug_python(target_file, max_attempts, interactive_mode):
    backup_file_path = backup_file(target_file) 

    for attempt in range(1, max_attempts + 1):
        success, output = run_python_file(target_file)
        if success:
            print("The Python script ran successfully!")
            break
        else:
            print(f"\nAttempt {attempt}: Error encountered while running the script:")
            print(highlight(output.decode("utf-8"), PythonLexer(), TerminalFormatter())) 

            with open(target_file, "r") as f:
                original_code = f.read() 

            fixed_code = fix_python_code(original_code, output.decode("utf-8"))
            print(f"GPT-4 suggested fix:\n")
            print(highlight(fixed_code, PythonLexer(), TerminalFormatter())) 

            if interactive_mode:
                user_input = input("Do you want to apply this fix? [Y/n]: ").lower()
                if user_input not in ["y", "yes", ""]:
                    print("Skipping the suggested fix.")
                    continue 

            with open(target_file, "w") as f:
                f.write(fixed_code) 

            diff = compare_files(backup_file_path, target_file)
            logging.info(f"Attempt {attempt}:\nError output: {output.decode('utf-8')}\nSuggested fix:\n{fixed_code}\nDiff:\n{diff}\n") 

    if not success:
        print("Maximum number of attempts reached. Please try fixing the script manually or run AutoDebug again.") 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-debug Python script using GPT-4.")
    parser.add_argument("target_file", help="The Python script to be debugged.")
    parser.add_argument("--max_attempts", type=int, default=5, help="The maximum number of attempts to fix the script.")
    parser.add_argument("--interactive", action="store_true", help="Enable interactive mode to approve or reject suggested fixes.")
    args = parser.parse_args() 

    target_file = args.target_file
    max_attempts = args.max_attempts
    interactive_mode = args.interactive 

    if not Path(target_file).is_file():
        print("Error: The specified file does not exist.")
        sys.exit(1) 

    # Check and install dependencies
    dependencies = ["pygments", "difflib", "openai"]
    missing_dependencies = check_dependencies(dependencies)
    if missing_dependencies:
        print(f"Missing dependencies: {', '.join(missing_dependencies)}")
        user_input = input("Do you want to install them now? [Y/n]: ").lower()
        if user_input in ["y", "yes", ""]:
            install_dependencies(missing_dependencies)
        else:
            print("Error: Required dependencies not installed.")
            sys.exit(1) 

    auto_debug_python(target_file, max_attempts, interactive_mode)
