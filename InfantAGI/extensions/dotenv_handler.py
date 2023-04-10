#dotenv_handler.py v1.1.0 

from dotenv import load_dotenv 

def load_dotenv_extensions(dotenv_files):
    """
    Load environment variables from the provided dotenv files. 

    Args:
        dotenv_files (list): A list of dotenv files to load.
    """
    for dotenv_file in dotenv_files:
        load_dotenv(dotenv_file)
