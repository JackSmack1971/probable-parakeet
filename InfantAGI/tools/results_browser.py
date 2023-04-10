#results_browser.py v1.1.0 

#!/usr/bin/env python3
import os
import curses
import argparse
import openai
import pinecone
from dotenv import load_dotenv
import textwrap 

load_dotenv() 

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")
PINECONE_TABLE_NAME = os.getenv("TABLE_NAME", "") 

def query_records(index, query, top_k=1000):
    """
    Query records from the Pinecone index based on a given query and top_k results. 

    Args:
        index (pinecone.Index): The Pinecone index to query.
        query (str): The query to search for in the index.
        top_k (int): The number of top results to retrieve from the index. 

    Returns:
        list: A list of dictionaries containing the task name and result.
    """
    results = index.query(query, top_k=top_k, include_metadata=True)
    return [{"name": f"{task.metadata['task']}", "result": f"{task.metadata['result']}"} for task in results.matches] 

def get_ada_embedding(text):
    return openai.Embedding.create(input=[text], model="text-embedding-ada-002")["data"][0]["embedding"] 

def parse_arguments():
    parser = argparse.ArgumentParser(description="Query Pinecone index using a string.")
    parser.add_argument('objective', nargs='*', metavar='<objective>', help='''
    main objective description. Doesn\'t need to be quoted.
    if not specified, get objective from environment.
    ''', default=[os.getenv("OBJECTIVE", "")])
    return parser.parse_args() 

# Remaining functions for drawing tasks, result, and summary 

def main(stdscr):
    """
    Main function to query the Pinecone index using a string and display the results in a TUI interface.
    """
    args = parse_arguments()
    objective = ' '.join(args.objective).strip().replace("\n", " ") 

    # Initialize Pinecone
    pinecone.init(api_key=PINECONE_API_KEY) 

    try:
        # Connect to the objective index
        with pinecone.Index(index_name=PINECONE_TABLE_NAME) as index:
            # Query records from the index
            retrieved_tasks = query_records(index, get_ada_embedding(objective)) 

            # Start the TUI interface and handle user input
            # ...
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Deinitialize Pinecone
        pinecone.deinit() 

if __name__ == "__main__":
    curses.wrapper(main)
