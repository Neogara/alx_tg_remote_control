import datetime
import os
import sys

import telebot.types
from PIL import ImageGrab
from dotenv import load_dotenv
from telebot.types import ReplyKeyboardMarkup, \
    KeyboardButton
import psutil

load_dotenv()

import assistant_utils
import os_utils

telegram_bot_token = os.getenv('telegram_bot_token')
tele_bot = telebot.TeleBot(telegram_bot_token)
auth_ids = [int(i) for i in os.getenv('auth_ids').strip("[], ").split(',')]


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
    assistant_utils.check_assistant(message, tele_bot)


@tele_bot.message_handler(commands=['reset_assistant'])
@authorize
def handle_reset_assistant(message):
    assistant_utils.reset_assistant(message, tele_bot)


@tele_bot.message_handler(commands=['get_screenshot'])
@authorize
def handle_get_screenshot(message):
    screenshot = ImageGrab.grab()
    tele_bot.send_photo(message.chat.id, screenshot)


@tele_bot.message_handler(commands=['cmd'])
@authorize
def handle_CMD_message(message):
    cmd_send_command = ' '.join(message.text.split()[1:])
    cmd_output = os_utils.cmd_send_command(cmd_send_command)
    tele_bot.send_message(message.chat.id, cmd_output)


@tele_bot.message_handler(commands=['remote_update_code'])
def handle_remote_update_code_command(message):
    prefix = "[remote_update_code] "
    print(f"{prefix}Remote update code command received from {message.from_user.first_name} ({message.from_user.id})")
    git_update_output = os_utils.cmd_send_command('git pull')
    print(f"{prefix}Git update output: {git_update_output}")
    if not git_update_output.startswith("Already up to date."):
        tele_bot.send_message(message.chat.id, 'Already up-to-date.')
    else:
        tele_bot.send_message(message.chat.id, git_update_output)
        tele_bot.send_message(message.chat.id, 'Restarting bot ..')
        os.execl(sys.executable, '"{}"'.format(sys.executable), *sys.argv)
        sys.exit(0)


@tele_bot.message_handler(commands=['start'])
@authorize
def handle_start(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('/get_screenshot', ))
    keyboard.add(KeyboardButton('/check_assistant'))
    keyboard.add(KeyboardButton('/reset_assistant'))
    keyboard.add(KeyboardButton('/remote_update_code'))

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
        telebot.types.BotCommand("/reset_assistant", "Reboot assistant"),
        telebot.types.BotCommand("/check_assistant", "Get assistant program screenshot"),
        telebot.types.BotCommand("/cmd", "Send CMD command /cmd [command]"),
        telebot.types.BotCommand("/remote_update_code", "Remote update code"),

    ]
    tele_bot.set_my_commands(bot_commands)

    print(f"Bot Commands:")
    for bot_commant_item in tele_bot.get_my_commands(scope=None, language_code=None):
        print(f"\t /{bot_commant_item.command} : {bot_commant_item.description}")

    tele_bot.send_message(auth_ids[0], "Telegram Bot ready to receive commands")

    tele_bot.infinity_polling().infinity_polling()
