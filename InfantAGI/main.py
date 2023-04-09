import time
import logging
from collections import deque
from config import (
    TASK_LIST_HEADER,
    TASK_LIST_FOOTER,
    NEXT_TASK_HEADER,
    NEXT_TASK_FOOTER,
    TASK_RESULT_HEADER,
    TASK_RESULT_FOOTER,
    PINECONE_NAMESPACE,
    SLEEP_TIME,
) 

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
) 

task_list = deque()  # This should be populated with tasks 

while task_list:
    try:
        # Print the task list
        print(TASK_LIST_HEADER + "\n*****TASK LIST*****\n" + TASK_LIST_FOOTER)
        for t in task_list:
            print(str(t["task_id"]) + ": " + t["task_name"]) 

        # Step 1: Pull the first task
        task = task_list.popleft()
        print(NEXT_TASK_HEADER + "\n*****NEXT TASK*****\n" + NEXT_TASK_FOOTER)
        print(str(task["task_id"]) + ": " + task["task_name"]) 

        # Send to execution function to complete the task based on the context
        result = execution_agent(OBJECTIVE, task["task_name"])
        this_task_id = int(task["task_id"])
        print(TASK_RESULT_HEADER + "\n*****TASK RESULT*****\n" + TASK_RESULT_FOOTER)
        print(result) 

        # Step 2: Enrich result and store in Pinecone
        enriched_result = {
            "data": result
        }  # This is where you should enrich the result if needed
        result_id = f"result_{task['task_id']}"
        vector = get_ada_embedding(
            enriched_result["data"]
        )  # get vector of the actual result extracted from the dictionary
        index.upsert(
            [(result_id, vector, {"task": task["task_name"], "result": result})],
            namespace=PINECONE_NAMESPACE,
        ) 

        # Step 3: Create new tasks and reprioritize task list
        new_tasks = task_creation_agent(
            OBJECTIVE,
            enriched_result,
            task["task_name"],
            [t["task_name"] for t in task_list],
        ) 

        for new_task in new_tasks:
            task_id_counter += 1
            new_task.update({"task_id": task_id_counter})
            add_task(new_task)
        prioritization_agent(this_task_id) 

    except Exception as e:
        logging.error(f"Error occurred while processing task {task['task_id']}: {e}") 

time.sleep(SLEEP_TIME)  # Sleep before checking the task list again
