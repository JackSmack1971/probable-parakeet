    # Print the task list
    print("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
    for t in task_list:
        print(str(t["task_id"]) + ": " + t["task_name"])

    # Step 1: Pull the first task
    task = task_list.popleft()
    print("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
    print(str(task["task_id"]) + ": " + task["task_name"])

    # Send to execution function to complete the task based on the context
    result = execution_agent(OBJECTIVE, task["task_name"])
    this_task_id = int(task["task_id"])
    print("\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m")
    print(result)

    # Step 2: Enrich result and store in Pinecone
    enriched_result = {
        "data": result
    }  # This is where you should enrich the result if needed
    result_id = f"result_{task['task_id']}"
    vector = get_ada_embedding(
        enriched_result["data"]
    )  # get vector of the actual result extracted from the dictionary
    index.upsert(
        [(result_id, vector, {"task": task["task_name"], "result": result})],
        namespace=OBJECTIVE
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

time.sleep(1)  # Sleep before checking the task list again
