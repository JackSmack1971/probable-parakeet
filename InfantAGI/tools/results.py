#results.py v1.1.0 

#!/usr/bin/env python3
import os
import argparse
import openai
import pinecone
from dotenv import load_dotenv 

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
        list: A list of formatted result strings.
    """
    results = index.query(query, top_k=top_k, include_metadata=True)
    return [f"{task.metadata['task']}:\n{task.metadata['result']}\n------------------" for task in results.matches] 

def get_ada_embedding(text):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model="text-embedding-ada-002")["data"][0]["embedding"] 

def main():
    """
    Main function to query the Pinecone index using a string.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Query Pinecone index using a string.")
    parser.add_argument('objective', nargs='*', metavar='<objective>', help='''
    main objective description. Doesn\'t need to be quoted.
    if not specified, get objective from environment.
    ''', default=[os.getenv("OBJECTIVE", "")])
    parser.add_argument('--top_k', type=int, default=1000, help='Number of top results to retrieve from Pinecone index.')
    args = parser.parse_args() 

    # Initialize Pinecone
    pinecone.init(api_key=PINECONE_API_KEY) 

    try:
        # Connect to the objective index
        with pinecone.Index(index_name=PINECONE_TABLE_NAME) as index:
            # Query records from the index
            query = get_ada_embedding(' '.join(args.objective).strip())
            retrieved_tasks = query_records(index, query, top_k=args.top_k)
            for r in retrieved_tasks:
                print(r)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Deinitialize Pinecone
        pinecone.deinit() 

if __name__ == "__main__":
    main()
