import SQL
import prettytable as pt
import re
import decimal
from PIL import Image

class Input:
    Message: str
    Parameter: str


class Command:
    message: str
    name: str
    SQL: str
    Description: str
    inputs: list[Input]
    department: list[int]
    Type: str
    path: [None, str]

    def __init__(self):
        self.message = ""

    def __repr__(self):
        return f"{self.name}, {self.Description}, {self.SQL}"

    def run_command(self, parameter, update):
        command = self
        header, data, types = SQL.SQLCommand(command, parameter)
        pic = -1
        pic_data = []
        for i in range(len(header)):
            if header[i] == "Gambar":
                pic = i
                header.pop(i)
        table = pt.PrettyTable(header)
        for i, head in enumerate(header):
            table.align[head] = "l"
            if types == decimal.Decimal:
                table.align[head] = "r"
        for i, data in enumerate(data):
            if pic != -1:
                pic_data.append(data[pic])
                data.pop(pic)
            if len(data) != 0:
                table.add_row(data)
        if len(header) != 0 and len(pic_data) == 0:
            update.message.reply_text(
                f'{table}'.replace("|", "").replace("-", "").replace("+", ""))
        if len(pic_data) != 0:
            data = f'{table}'.split("\n")
            data = data[3:-1]
            for index, i in enumerate(pic_data):

                try:
                    i = i.split("\\")
                    i[-1] = re.sub("^\d*", "", i[-1])
                    i = "\\".join(i)
                    image = Image.open(i)
                    image.resize((300, 300))
                    image.save("temp.jpg")
                    update.message.reply_photo(open("temp.jpg", "rb"))

                except:
                    update.message.reply_text("Photo tidak ada")
                if len(data) != 0:
                    update.message.reply_text(data[index][1:-1])


class SubBlock:
    name: str
    commands: list[Command]
    department: list[int]

    def __repr__(self):
        ret = f"{self.name}"
        for i, command in enumerate(self.commands):
            ret += f"\n {command.__repr__()}"
        return ret


def loadXML():
    from bs4 import BeautifulSoup
    with open("setting.xml", "r") as f:
        data = f.read()
    data = data.replace("&", " &amp; ").replace(" <> ", " &lt;&gt; ").replace(" < ", " &lt; ").replace(
        " > ", " &gt; ").replace("'", "&apos;").replace(
        '"', "&quot;")
    bs_data = BeautifulSoup(data, "xml").findChild("Setting")
    block = []
    for sub_block in bs_data.findChildren("SubBlock", recursive=False):
        sub_block_c = SubBlock()
        sub_block_c.name = sub_block.findChild("Name").text
        sub_block_c.department = [int(x) for x in sub_block.findChild("Department").text.split(";")]
        sub_block_c.commands = []
        for command in sub_block.findChildren("Command", recursive=False):
            command_c = Command()
            command_c.name = command.findChild("Name").text
            command_c.SQL = command.findChild("SQL").text
            command_c.Description = command.findChild(
                "Description").text if command.findChild(
                "Description") is not None else "No desc"
            command_c.Type = command.findChild("Type").text
            if command_c.Type == "Access":
                command_c.path = command.findChild("FilePath").text
            else:
                command_c.path = None
            command_c.department = sub_block_c.department
            command_c.inputs = []
            for inputs in command.findChildren("Input", recursive=False):
                inputs_c = Input()
                inputs_c.Message = inputs.findChild("Message").text
                inputs_c.Parameter = inputs.findChild("Parameter").text
                command_c.inputs.append(inputs_c)
            sub_block_c.commands.append(command_c)
        block.append(sub_block_c)
    bot_id = bs_data.findChild("BotID").text
    department = bs_data.findChild("Department").text.split(";")
    return bot_id, block, department
