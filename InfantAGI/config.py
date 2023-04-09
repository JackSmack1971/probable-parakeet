import os

# ANSI escape codes
TASK_LIST_HEADER = os.environ.get("TASK_LIST_HEADER", "\033[95m\033[1m")
TASK_LIST_FOOTER = os.environ.get("TASK_LIST_FOOTER", "\033[0m\033[0m")
NEXT_TASK_HEADER = os.environ.get("NEXT_TASK_HEADER", "\033[92m\033[1m")
NEXT_TASK_FOOTER = os.environ.get("NEXT_TASK_FOOTER", "\033[0m\033[0m")
TASK_RESULT_HEADER = os.environ.get("TASK_RESULT_HEADER", "\033[93m\033[1m")
TASK_RESULT_FOOTER = os.environ.get("TASK_RESULT_FOOTER", "\033[0m\033[0m")

# Pinecone namespace
PINECONE_NAMESPACE = os.environ.get("PINECONE_NAMESPACE", "default_namespace")

# Sleep time between task list checks
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 1))
