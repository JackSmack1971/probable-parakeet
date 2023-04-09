InfantAGI: Enhanced Task Management System
InfantAGI is a Python-based task management system that has been refined to offer more functionality and efficiency. The system, powered by OpenAI and Pinecone APIs, creates, prioritizes, and executes tasks, refining them based on previous results and a predefined objective. InfantAGI leverages OpenAI's natural language processing (NLP) capabilities for task creation and Pinecone for context-aware storage and retrieval of task results.

Table of Contents
Improvements
How It Works
Usage
Supported Models
Warning
Improvements
The InfantAGI system has been updated with the following enhancements:

Error handling: Robust error handling and informative messages have been added to the script, ensuring a smooth user experience.
Code optimization: The code has been refactored for improved readability, maintainability, and performance.
Configurable settings: The system has been made more flexible by allowing users to configure settings such as the OpenAI model, the initial task, and the main objective.
Environment variable handling: The environment variable handling has been improved to support the use of multiple .env files, providing greater flexibility in managing settings.
How It Works
The InfantAGI system performs the following steps in a continuous loop:

Retrieves the first task from the task list.
Executes the task using OpenAI's API, considering the context.
Stores the enriched result in Pinecone.
Generates and reprioritizes new tasks based on the objective and the previous task result.
The OpenAI API is utilized in the execution_agent() function to complete tasks, task_creation_agent() function to create new tasks, and prioritization_agent() function to reprioritize the task list.

Pinecone is used to store and retrieve task results, maintaining context. The script creates a Pinecone index based on the table name specified in the .env file.

Usage
To use InfantAGI, follow these steps:

Clone the repository: git clone https://github.com/yoheinakajima/infantagi.git and cd into the cloned directory.
Install the required packages: pip install -r requirements.txt
Copy the .env.example file to .env: cp .env.example .env. Set the necessary variables in the .env file.
Configure the following variables in the .env file:
OpenAI and Pinecone API keys: OPENAI_API_KEY, OPENAI_API_MODEL, and PINECONE_API_KEY
Pinecone environment: PINECONE_ENVIRONMENT
Table name for task results storage: TABLE_NAME
(Optional) Objective of the task management system: OBJECTIVE
(Optional) Initial task for the system: INITIAL_TASK
Run the script.
Optional values can also be specified using command-line arguments.

Supported Models
InfantAGI supports all OpenAI models, as well as Llama through Llama.cpp. The default model is gpt-3.5-turbo. To use a different model, specify it through OPENAI_API_MODEL or using the command line.

For Llama, download the latest version of Llama.cpp and follow the instructions to compile it. You will also need the Llama model weights. Then, link llama/main to llama.cpp/main and models to the folder with the Llama model
