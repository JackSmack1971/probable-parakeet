#infantagi v1.1.0 

InfantAGI 

InfantAGI is a suite of Python scripts designed to interact with and manage a cooperative AI system that utilizes OpenAI's API and Pinecone's vector search engine. The system helps users accomplish various objectives and tasks by leveraging the power of GPT models and the efficiency of Pinecone's index. 

Repository link: InfantAGI on GitHub 

Features 

• Query the Pinecone index to search for relevant tasks and results. 

• Monitor the progress of objectives and tasks in real-time. 

• Manage environment configurations with ease using the .env files. 

• Support for different GPT models like GPT-4 and LLaMa. 

• Terminal-based user interface for better usability and navigation. 

Installation 

• Clone the repository: 

git clone https://github.com/JackSmack1971/probable-parakeet.git
cd probable-parakeet/InfantAGI 

• Create a virtual environment and activate it: 

python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate` 

• Install the required dependencies: 

pip install -r requirements.txt 

• Set up your OpenAI API key and Pinecone API key in a .env file: 

OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key 

Replace your_openai_api_key and your_pinecone_api_key with your actual API keys. 

Usage 

Main script 

Run the main.py script to interact with the InfantAGI system: 

python main.py [options] 

Tools 

Several tools are provided in the /tools directory to facilitate interaction with the system: 

• monitor.py: Monitor the progress of objectives and tasks in real-time. 

• results.py: Query the Pinecone index to find relevant tasks and results. 

• results_browser.py: Browse and search through tasks and results using a terminal-based user interface. 

Extensions 

The /extensions directory contains several utility modules to enhance the functionality of the system: 

• argparseext.py: Extended argparse module for parsing command-line arguments. 

• dotenvext.py: dotenv extension for loading additional environment variables from files. 

• dotenv_handler.py: Handler for loading dotenv files. 

• ray_objectives.py: Cooperative objectives list storage using Ray. 

• ray_tasks.py: Cooperative tasks list storage using Ray.
