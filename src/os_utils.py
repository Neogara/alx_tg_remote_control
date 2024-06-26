import subprocess
import time

import psutil


def kill_process_by_pid(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        return True, f"Process with PID {pid} has been terminated."
    except psutil.NoSuchProcess:
        return False, "Process with PID {pid} not found."

    except psutil.AccessDenied:
        return False, f"No permission to terminate process with PID {pid}."


def find_process_by_name(process_name):
    try:
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == process_name:
                return process.info
    except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
        print(f"Error occurred while trying to find process by name: {e}")
    return None


def run_program(program_path):
    try:
        subprocess.Popen(program_path)
        time.sleep(5)
        return True, f"Program '{program_path}' started successfully."
    except FileNotFoundError:
        return False, f"Program '{program_path}' not found."


def cmd_send_command(command):
    try:
        process = subprocess.run(command,
                                 shell=True,
                                 check=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True,
                                 encoding="cp866")

        output = process.stdout

        if not output:
            output = f"No output from command: '{command}'"

        print(f"[cmd command]: {command} -> {output}")
        return output

    except Exception as e:
        error_message = str(e)
        print(f"[cmd command] ERROR: {command} -> {error_message}")
        return error_message
