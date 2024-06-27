import time
from functools import wraps

from dotenv import load_dotenv

load_dotenv()

import datetime
import os
import sys
from PIL import ImageGrab
import telebot.types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

import assistant_utils
from configs.assistant_config import AssistantInstances
import os_utils

telegram_bot_token = os.getenv('telegram_bot_token')
tele_bot = telebot.TeleBot(telegram_bot_token)
auth_ids = [int(i) for i in os.getenv('auth_ids').strip("[], ").split(',')]
MAX_MESSAGE_LENGTH = 4096


def authorize(func):
    def wrapper(message):
        if (message.from_user.id in auth_ids):
            func(message)
        else:
            date = datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{date}] Unauthorized | {message.from_user.first_name} ({message.from_user.id}) -> {message.text}")
            tele_bot.send_message(message.chat.id,
                                  f'{message.from_user.first_name} : You are not authorized')

    return wrapper


@tele_bot.message_handler(commands=['check_assistant'])
@authorize
def handle_check_assistant(message):
    select_assistant_name = ' '.join(message.text.split()[1:]).strip()
    select_assistant_instance = AssistantInstances.get_assistant_instance_by_name(select_assistant_name)

    if select_assistant_instance is None:
        return_message = f"Assistant '{select_assistant_name}' not found."
        tele_bot.send_message(message.chat.id, return_message)
        return

    assistant_utils.check_assistant(message, tele_bot, select_assistant_instance)


@tele_bot.message_handler(commands=['reset_assistant'])
@authorize
def handle_reset_assistant(message):
    select_assistant_name = ' '.join(message.text.split()[1:]).strip()
    select_assistant_instance = AssistantInstances.get_assistant_instance_by_name(select_assistant_name)

    if select_assistant_instance is None:
        return_message = f"Assistant '{select_assistant_name}' not found."
        tele_bot.send_message(message.chat.id, return_message)
        return

    assistant_utils.reset_assistant(message, tele_bot, select_assistant_instance)


@tele_bot.message_handler(commands=['get_screenshot'])
@authorize
def handle_get_screenshot(message):
    screenshot = ImageGrab.grab()
    tele_bot.send_photo(message.chat.id, screenshot)


def is_long_text(text):
    return len(text) > MAX_MESSAGE_LENGTH


def split_long_text(text):
    return [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]


@tele_bot.message_handler(commands=['cmd'])
@authorize
def handle_CMD_message(message):
    cmd_send_command = ' '.join(message.text.split()[1:])
    cmd_output = os_utils.cmd_send_command(cmd_send_command)
    cmd_output.spli
    if is_long_text(cmd_output):
        for cmd_output_part in split_long_text(cmd_output):
            time.sleep(0.2)
            tele_bot.send_message(message.chat.id, cmd_output_part)
    else:
        tele_bot.send_message(message.chat.id, cmd_output)


@tele_bot.message_handler(commands=['restart_pc'])
@authorize
def handle_restart_pc(message):
    os_utils.cmd_send_command('shutdown /r /t 0')
    tele_bot.send_message(message.chat.id, 'Restarting PC.. wait 1 minute for restarting')


@tele_bot.message_handler(commands=['remote_update_code'])
def handle_remote_update_code_command(message):
    prefix = "[remote_update_code] "
    print(f"{prefix}Remote update code command received from {message.from_user.first_name} ({message.from_user.id})")
    git_update_output = os_utils.cmd_send_command('git pull')
    print(f"{prefix}Git update output: {git_update_output}")
    if git_update_output.startswith("Already up to date."):
        tele_bot.send_message(message.chat.id, 'Already up-to-date.')
    else:
        tele_bot.send_message(message.chat.id, git_update_output)
        tele_bot.send_message(message.chat.id, 'Restarting bot ..')
        os.execl(sys.executable, '"{}"'.format(sys.executable), *sys.argv)
        sys.exit(0)


@tele_bot.message_handler(commands=['assistant_control'])
@authorize
def handle_assistant_control(message):
    assistant_control_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    assistant_names = AssistantInstances.get_names()
    for assistant_name_item in assistant_names:
        assistant_control_keyboard.add(KeyboardButton(f"/check_assistant {assistant_name_item}"))
        assistant_control_keyboard.add(KeyboardButton(f"/reset_assistant {assistant_name_item}"))
    assistant_control_keyboard.add("/start_page")
    tele_bot.reply_to(message, 'Hello, ' + message.from_user.first_name, reply_markup=assistant_control_keyboard)


@tele_bot.message_handler(commands=['start'])
@authorize
def handle_start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(KeyboardButton("/start"))
    keyboard.add(KeyboardButton("/get_screenshot"))

    keyboard.add(KeyboardButton("/assistant_control"))

    keyboard.add(KeyboardButton("/cmd"))
    keyboard.add(KeyboardButton("/restart_pc"))

    keyboard.add(KeyboardButton("/remote_update_code"))
    tele_bot.reply_to(message, 'Hello, ' + message.from_user.first_name, reply_markup=keyboard)


@tele_bot.message_handler(content_types=['text'])
@authorize
def base_handler(message):
    date = datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{date}] {message.from_user.first_name} ({message.from_user.id}) -> {message.text}")


if __name__ == '__main__':
    print(f"Telegram Bot Start")
    tele_bot_info = tele_bot.get_me()
    print(f"Bot Username: {tele_bot_info.username}"
          f"Bot Id: {tele_bot_info.id}")

    bot_commands = [
        telebot.types.BotCommand("/start", "Start"),
        telebot.types.BotCommand("/get_screenshot", "Get full size screenshot"),

        telebot.types.BotCommand("/assistant_control", "Assistant control menu"),

        telebot.types.BotCommand("/cmd", "Send CMD command /cmd [command]"),
        telebot.types.BotCommand("/restart_pc", "Restart PC with CMD. Wait 1 minute"),

        telebot.types.BotCommand("/remote_update_code", "Remote update code"),
    ]
    tele_bot.set_my_commands(bot_commands)

    print(f"Bot Commands:")
    for bot_commant_item in tele_bot.get_my_commands(scope=None, language_code=None):
        print(f"\t /{bot_commant_item.command} : {bot_commant_item.description}")

    tele_bot.send_message(auth_ids[0], "Telegram Bot ready to receive commands")

    tele_bot.infinity_polling().infinity_polling()
