from dotenv import load_dotenv

def load_dotenv_extensions(dotenv_files):
    for dotenv_file in dotenv_files:
        try:
            load_dotenv(dotenv_file)
        except IOError as e:
            print(f"Unable to load {dotenv_file}: {e}")
        except Exception as e:
            print(f"An error occurred while loading {dotenv_file}: {e}")
