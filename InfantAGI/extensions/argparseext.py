#argparseext.py v1.1.0
import os
import sys
import argparse


def parse_dotenv_extensions(argv):
    """
    Extracts the env filenames from the '-e' flag and returns them as a list.
    """
    env_argv = []
    if '-e' in argv:
        tmp_argv = argv[argv.index('-e') + 1:]
        parsed_args = []
        for arg in tmp_argv:
            if arg.startswith('-'):
                break
            parsed_args.append(arg)
        env_argv = ['-e'] + parsed_args 

    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', nargs='+', help='''
    filenames for additional env variables to load
    ''', default=os.getenv("DOTENV_EXTENSIONS", "").split(' ')) 

    return parser.parse_args(env_argv).env


def load_dotenv_extensions(dotenv_extensions):
    """
    Loads dotenv extensions if provided.
    """
    if dotenv_extensions:
        from extensions.dotenvext import load_dotenv_extensions
        load_dotenv_extensions(dotenv_extensions)


def print_error(message):
    print("\033[91m\033[1m" + message + "\n\033[0m\033[0m")


def parse_arguments():
    dotenv_extensions = parse_dotenv_extensions(sys.argv)
    load_dotenv_extensions(dotenv_extensions)
    dotenv_extensions_default = os.getenv("DOTENV_EXTENSIONS", "").split(' ') 

    parser = argparse.ArgumentParser(
        add_help=False,
    )
    # Define the parser arguments
    ... 

    args = parser.parse_args() 

    # Extract arguments and validate
    ... 

    return objective, initial_task, openai_api_model, dotenv_extensions
