import time

import os
import pygetwindow as gw
from os_utils import kill_process_by_pid, find_process_by_name, run_program
from PIL import ImageGrab

# from configs.assistant_config import assistant_process_name, assistant_program_path, assistant_window_name, \
#     use_assistant_pre_check

from configs.assistant_config import AssistantConfig, AssistantInstance


def take_screenshot_assistant(assistant_instance: AssistantInstance):
    windows = gw.getWindowsWithTitle(assistant_instance.window_name)
    if windows is None:
        return False, f"No window found for process '{assistant_instance.window_name}'", None

    screenshots = []
    for window in windows:
        try:
            print(window)
            try:
                window.activate()
            except Exception as e:
                print(f"Error occurred while activating window: {e}")

            time.sleep(0.5)
            screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.right, window.bottom))
            if screenshot.getbbox():
                screenshots.append(screenshot)

            window.minimize()

        except Exception as e:
            print(window)
            print(f"Error occurred while taking screenshot: {e}")

    if len(screenshots) == 0:
        return False, f"No screenshots found for process '{assistant_instance.window_name}'", None

    return True, "Screenshots taken", screenshots


def reset_assistant(message, tele_bot, assistant_instance: AssistantInstance):
    print(message)
    print("/reset_assistant")

    process_info = find_process_by_name(assistant_instance.process_name)
    if process_info is None:
        return_message = f"Process with name {assistant_instance.process_name} not found."
        tele_bot.send_message(message.chat.id, return_message)

    return_message = f"Process with name {assistant_instance.process_name} found. PID: {process_info['pid']}"
    tele_bot.send_message(message.chat.id, return_message)

    kill_status, kill_process_message = kill_process_by_pid(process_info['pid'])
    tele_bot.send_message(message.chat.id, kill_process_message)

    if not kill_status:
        return_message = f"Cam't kill process with name {assistant_instance.process_name}." \
                         f"\n" \
                         f"{kill_process_message}"
        tele_bot.reply_to(message, return_message)

    run_status, run_process_message = run_program(assistant_instance.program_path)
    tele_bot.send_message(message.chat.id, run_process_message)

    if not run_status:
        return_message = f"Can't run {assistant_instance.program_path}." \
                         f"\n" \
                         f"{run_process_message}"
        tele_bot.send_message(message.chat.id, return_message)
        return

    return_message = f"Command {assistant_instance.program_path} executed successfully."
    tele_bot.send_message(message.chat.id, return_message)


def check_assistant(message, tele_bot, assistant_instance: AssistantInstance):
    print(message)
    process_info = find_process_by_name(assistant_instance.process_name)
    if process_info is None:
        return_message = f"Process with name '{assistant_instance.process_name}' not found."
        tele_bot.reply_to(message, return_message)
    else:
        return_message = f"Process with name '{assistant_instance.process_name}' found.\n" \
                         f"PID: {process_info['pid']}"
        tele_bot.send_message(message.chat.id, return_message)

    tele_bot.send_message(message.chat.id, f"Try to run program\n"
                                           f"-> {assistant_instance.program_path}")
    run_program(assistant_instance.program_path)

    take_screenshot_status, take_screenshot_message, screenshots = take_screenshot_assistant(assistant_instance)
    if not take_screenshot_status:
        return_message = f"Can't take screenshot." \
                         f"\n" \
                         f"{take_screenshot_message}"
        tele_bot.send_message(message.chat.id, return_message)
        return

    for screenshot_item in screenshots:
        tele_bot.send_photo(message.chat.id, screenshot_item, caption=take_screenshot_message)
