import decimal

from telegram import ParseMode
import prettytable as pt
from xmlLoader import Command
import telegram
import telegram.ext
import re

Context = telegram.ext.callbackcontext.CallbackContext
Update = telegram.update.Update


class user:
    name: str
    id: int
    state: (None, Command)
    parameter: dict[str, str]
    message: str
    sys_name: str
    department: int

    def __init__(self, name, id, department, sys_name, message=""):
        self.department = department
        self.sys_name = sys_name
        self.message = ""
        self.name = name
        self.id = id
        self.state = None
        self.parameter = {}

    def request_next_para(self, update: Update):
        if self.state is not None:
            if len(self.parameter) == len(self.state.inputs):
                self.state.run_command(self.parameter, update)
                self.state = None
            else:
                update.message.reply_text(
                    f"{self.state.inputs[len(self.parameter)].Message}")

    def process_non_command(self, update: Update, context):
        if self.state is None:
            update.message.reply_text(
                "Invalid Input, Please run a command, /help to get all command")
        else:
            self.parameter[self.state.inputs[
                len(self.parameter)].Parameter] = update.message.text
            self.request_next_para(update)

    def process_command(self, update: Update, context: Context, command):
        if command.message is not None and command.message != "":
            update.message.reply_text(f"{command.message}")
        self.parameter = {}
        para = re.split("[ _]", update.message.text)
        if len(para) != 1:
            if len(para) - 1 == len(command.inputs):
                for i, input in enumerate(command.inputs):
                    self.parameter[input.Parameter] = para[i + 1]
                command.run_command(self.parameter, update)
                self.state = None
            else:
                update.message.reply_text(
                    f"Number Of Input Invalid, expected : {len(command.inputs)}, got: {len(para) - 1}")
            return

        self.state = command
        self.request_next_para(update)


def process_user():
    f = open("User.txt")
    user_dic = {}
    for user_data in f.readlines():
        user_data = user_data.strip().split(";")
        user_dic[int(user_data[0])] = user(user_data[1], int(user_data[0]), int(user_data[2]), user_data[3])
    return user_dic
