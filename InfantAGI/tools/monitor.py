#!/usr/bin/env python3
import sys
import time
import curses
from pathlib import Path

# Add the parent directory to the system path to import extensions
sys.path.append(str(Path(__file__).resolve().parent.parent))
from extensions.ray_objectives import CooperativeObjectivesListStorage
from extensions.ray_tasks import CooperativeTaskListStorage


def print_buffer(stdscr, lines):
    """
    Clear the screen and print the provided lines.
    """
    stdscr.clear()
    for index, line in enumerate(lines):
        stdscr.addstr(index, 0, line)
    stdscr.refresh()


def main(stdscr):
    objectives = CooperativeObjectivesListStorage()

    while True:
        objectives_list = objectives.get_objective_names()
        buffer = []

        if not objectives_list:
            buffer.append("No objectives")

        for objective in objectives_list:
            buffer.append("-----------------")
            buffer.append(f"Objective: {objective}")
            buffer.append("-----------------")
            tasks = CooperativeTaskListStorage(objective)
            tasks_list = tasks.get_task_names()
            buffer.append("Tasks:")

            for task in tasks_list:
                buffer.append(f" * {task}")

            buffer.append("-----------------")

        print_buffer(stdscr, buffer)
        time.sleep(30)


curses.wrapper(main)
