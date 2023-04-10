#dotenvext.py v1.1.0 

from dotenv import load_dotenv 

def load_dotenv_extensions(dotenv_files):
    """
    Load environment variables from the provided dotenv files and handle exceptions. 

    Args:
        dotenv_files (list): A list of dotenv files to load.
    """
    for dotenv_file in dotenv_files:
        try:
            load_dotenv(dotenv_file)
        except IOError as e:
            print(f"Unable to load dotenv file '{dotenv_file}': {e}")
        except Exception as e:
            print(f"An error occurred while loading dotenv file '{dotenv_file}': {e}")
