import xmlLoader
from user_process import process_user
import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from user_process import user as user_class

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

bot = None
Context = telegram.ext.callbackcontext.CallbackContext
Update = telegram.update.Update
logger = logging.getLogger("test")
user = {}
admin = {}
new_user = {}
block = []
command_dict = {}
department = []


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    update.message.reply_text("Error")


def not_command(update: Update, context: Context):
    print(update.effective_user.id, update.message.text)
    if update.effective_user.id in user.keys():
        if update.message.text[0] == "/":
            com = update.message.text.split("_")
            if com[0][1:] in command_dict:
                user[update.effective_user.id].process_command(update, context,
                                                               command_dict[
                                                                   com[0][1:]])
                return
        user[update.effective_user.id].process_non_command(update, context)
    else:
        new_user[update.effective_user.id] = update.effective_user.name
        update.message.reply_text(f"User Not Registered")


def check_access(id, command):
    return user[id].department in command.department


def create_process_command(command):
    def process_command(update: Update, context: Context):
        print(update.effective_user.id, update.message.text)
        if update.effective_user.id in user.keys():
            if not check_access(update.effective_user.id, command):
                update.message.reply_text("Access Denied")
            else:
                user[update.effective_user.id].process_command(update, context,
                                                               command)
        else:
            new_user[update.effective_user.id] = update.effective_user.name
            update.message.reply_text(f"User Not Registered")

    return process_command


def help(update: Update, context: Context):
    helpString = ""
    for subBlock in block:
        if user[update.effective_user.id].department in subBlock.department:
            helpString += f"*{subBlock.name}*\n"
            for command in subBlock.commands:
                helpString += f"/{command.name} - {command.Description}\n"
            helpString += "\n"
    if update.effective_user.id in admin:
        helpString += "*Admin*\n/AddUser\n/DeleteUser\n/UserList\n/UserUpdate\n/message\n"
    update.message.reply_text(helpString[:-1],
                              parse_mode=telegram.parsemode.ParseMode.MARKDOWN)


def load_admin():
    f = open("admin.txt")
    for line in f:
        line = line.split(";")
        admin[int(line[0])] = line[1]
    f.close()


def create_command_dict():
    for subBlock in block:
        for command in subBlock.commands:
            command_dict[command.name] = command


class new_user_list_print():
    end: str

    def __init__(self, end):
        self.end = end

    def __repr__(self):
        out = "New User List:"
        for i, id in enumerate(new_user):
            out += f"\n {i + 1}, {id}, {new_user[id]}"
        out += f"\n{self.end}"
        return out


def update_user():
    f = open("User.txt", "w")
    a = False
    for i in user:
        if a:
            f.write("\n")
        a = True
        f.write(f"{i};{user[i].name};{user[i].department};{user[i].sys_name}")
    f.close()


def create_process_admin(command):
    def process_command(update: Update, context: Context):
        print(update.effective_user.id, update.message.text)
        if update.effective_user.id in admin:
            user[update.effective_user.id].process_command(update, context,
                                                           command)
        else:
            update.message.reply_text(f"Admin Not Registered")

    return process_command


class AddUser(xmlLoader.Command):
    def __init__(self):
        xmlLoader.Command.__init__(self)

        name = "AddUser"
        inp = xmlLoader.Input()
        inp.Parameter = "numb"
        inp.Message = new_user_list_print("Input New User number")
        inp2 = xmlLoader.Input()
        inp2.Parameter = "Department"
        inp2.Message = "Department List"
        for i, depart in enumerate(department):
            inp2.Message += f"\n  {i + 1}. {department[i]}"
        inp2.Message += "\nPick department :"

        inp3 = xmlLoader.Input()
        inp3.Parameter = "sys_name"
        inp3.Message = "Input system name : "
        self.inputs = [inp, inp2, inp3]

    def run_command(self, parameter, update):
        global user
        index = 0
        try:
            index = int(parameter["numb"])
            dep_index = int(parameter["Department"]) - 1
        except IndexError:
            update.message.reply_text("Input Error")
            return

        id_new = list(new_user.keys())[index - 1]
        user[id_new] = user_class(new_user[id_new], id_new, dep_index,
                                  parameter["sys_name"])
        update_user()
        update.message.reply_text("User Added")


class user_list_print():
    end: str

    def __init__(self, end):
        self.end = end

    def __repr__(self):
        out = "User List:"
        for i, use in enumerate(user):
            out += f"\n {i + 1}, {user[use].name}, {department[user[use].department]}, {user[use].sys_name}"
        out += f"\n{self.end}"
        return out


class DeleteUser(xmlLoader.Command):
    def __init__(self):
        xmlLoader.Command.__init__(self)
        name = "DeleteUser"
        inp = xmlLoader.Input()
        inp.Parameter = "numb"
        inp.Message = user_list_print("Input User number")
        self.inputs = [inp]

    def run_command(self, parameter, update):
        global user
        index = 0
        try:
            index = int(parameter["numb"])
            a = list(user.keys())[index - 1]
        except:
            update.message.reply_text("Input Error")
            return

        user.pop(list(user.keys())[index - 1])
        update_user()
        update.message.reply_text("User Deleted")


class UserList(xmlLoader.Command):
    def __init__(self):
        super().__init__()
        self.name = "UserList"
        self.inputs = []
        self.message = user_list_print("")

    def run_command(self, parameter, update):
        pass


class UserUpdate(xmlLoader.Command):
    def __init__(self):
        super().__init__()
        self.name = "UserList"
        self.inputs = []
        inp = xmlLoader.Input()
        inp.Parameter = "numb"
        inp.Message = user_list_print("Input User number:")

        inp2 = xmlLoader.Input()
        inp2.Parameter = "Department"
        inp2.Message = "Department List"
        for i, depart in enumerate(department):
            inp2.Message += f"\n  {i + 1}. {department[i]}"
        inp2.Message += "\nPick department : (input 0 to not change)"

        inp3 = xmlLoader.Input()
        inp3.Parameter = "sys_name"
        inp3.Message = "Input system name : (input 0 to not change)"
        self.inputs = [inp, inp2, inp3]

    def run_command(self, parameter, update):
        numb = list(user.keys())[int(parameter["numb"]) - 1]
        print(numb)
        if parameter["sys_name"] != "0":
            user[numb].sys_name = parameter["sys_name"]
        if parameter["Department"] != "0":
            a = department[int(parameter["Department"]) - 1]
            user[numb].department = int(parameter["Department"]) - 1
            update_user()
            update.message.reply_text("User Updated")

class message_all(xmlLoader.Command):
    def __init__(self):
        super().__init__()
        self.name = "Message"
        inp = xmlLoader.Input()
        inp.Parameter = "message"
        inp.Message = "Input Message:"
        self.inputs = [inp]
    def run_command(self, parameter, update:Update):
        for use in user:
            bot.send_message(use, parameter["message"])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    botID, block, department = xmlLoader.loadXML()
    load_admin()
    print(admin)
    user = process_user()
    create_command_dict()
    bot = telegram.Bot(botID)
    updater = Updater(botID,
                      use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("AddUser", create_process_admin(AddUser())))
    dp.add_handler(
        CommandHandler("DeleteUser", create_process_admin(DeleteUser())))
    dp.add_handler(
        CommandHandler("UserUpdate", create_process_admin(UserUpdate())))
    dp.add_handler(CommandHandler("UserList", create_process_admin(UserList())))
    dp.add_handler(CommandHandler("message", create_process_admin(message_all())))
    for sub_block in block:
        for command in sub_block.commands:
            process_command = create_process_command(command)
            dp.add_handler(CommandHandler(command.name, process_command))

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, not_command))

    # log all errors
    #dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
