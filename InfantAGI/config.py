#config.py v1.1.0 

import os 

# ANSI escape codes for displaying colored headers and footers
TASK_LIST_HEADER = os.environ.get("TASK_LIST_HEADER", "\033[95m\033[1m")
TASK_LIST_FOOTER = os.environ.get("TASK_LIST_FOOTER", "\033[0m\033[0m")
NEXT_TASK_HEADER = os.environ.get("NEXT_TASK_HEADER", "\033[92m\033[1m")
NEXT_TASK_FOOTER = os.environ.get("NEXT_TASK_FOOTER", "\033[0m\033[0m")
TASK_RESULT_HEADER = os.environ.get("TASK_RESULT_HEADER", "\033[93m\033[1m")
TASK_RESULT_FOOTER = os.environ.get("TASK_RESULT_FOOTER", "\033[0m\033[0m") 

# Pinecone namespace for storing results
PINECONE_NAMESPACE = os.environ.get("PINECONE_NAMESPACE", "default_namespace") 

# Sleep time (in seconds) between task list checks
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 1)) 

# Initial value for the task_id_counter
TASK_ID_COUNTER = int(os.environ.get("TASK_ID_COUNTER", 0))
