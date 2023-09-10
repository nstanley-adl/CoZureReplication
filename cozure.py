import re
from os.path import exists
from typing import List


def convert_to_file_name(file_name: str) -> str:
    file_name = str(file_name).replace(" ", "-")
    return "".join(x for x in file_name if x.isalnum())



class Command:
    """
    Smallest building block, representing a single command.
    Contains a unique index, and command text.
    The text may contain parameters, these are substituted at runtime.
    """

    def __init__(self, index: int, text: str):
        self.index = index
        self.text = text

    def execute_command(self) -> None:
        print(f"Executing command. idx:{self.index} cmd:{self.text}")

        pattern = re.compile(r"([\<|\[|\{\(](\S*)[\>|\]|\}|\)])", re.MULTILINE)
        matches = re.findall(pattern, self.text)

        parameter_names = [match[1] for match in matches if match[1]]
        number_of_params = len(parameter_names)
        param_options = []
        options_per_param = []

        # load options for parameters
        for name in parameter_names:
            file_name = "params/" + convert_to_file_name(name) + ".csv"

            # create the file if not exists
            if not exists(file_name):
                file = open(file_name, "x")
                file.close()

            file = open(file_name, "r")
            ops = [line.rstrip() for line in file]
            param_options.append(ops)
            options_per_param.append(len(ops))

        # attempt all until successful
        current_attempt = [0, 0, 0]
        combinations = 1
        for option_count in options_per_param:
            combinations *= option_count

        for _ in range(combinations):
            for i in range(number_of_params):
                if current_attempt[i] < options_per_param[i] - 1:
                    current_attempt[i] += 1
                    break
                else:
                    current_attempt[i] = 0
            # print(current_attempt)
            # try sub
            words = re.split(pattern, self.text)
            j = 0
            for k in range(len(words)):
                word: str = words[k]
                if re.match(pattern, word):
                    words[k] = param_options[j][current_attempt[j]]
                    words[k + 1] = ""  # clear next
                    j += 1
            print("> " + "".join(words))
            # TODO: invoke command & break if successful.


class Activity:
    """
    An ordered subset of commands which are combined to achieve an objective.
    Contains a name, an index, and list of commands.
    An activity must be meaningful, commands by not arbitrarily form an activity.
    """

    def __init__(self, name: str, index: int, commands: List[Command]):
        self.name = name
        self.index = index
        self.commands = commands

    def execute_activity(self) -> None:
        print(f"Executing activity. idx:{self.index} name:{self.name}")
        for command in self.commands:
            command.execute_command()


class SecurityAttribute:
    """
    A security attribute is an ordered set of multiple activities.
    Contains a name, an index, and list of activities.
    """

    def __init__(self, name: str, index: int, activities: List[Activity]):
        self.name = name
        self.index = index
        self.activities = activities

    def add_activity(self, activity: Activity) -> None:
        self.activities.append(activity)


class CommandStore:
    """
    Represents a file containing all commands.
    Use a command store to get and fetch commands.

    FILE FORMAT:
    (command_index),(command_text)
    (command_index),(command_text)
    (command_index),(command_text)
    """

    def __init__(self, file_name: str):
        """
        Attempts to load an existing command store.
        If the store is not found, a new one is created.
        :param file_name: the file to save the command store in.
        """
        self.store = {}
        self.file_name = file_name

        if not exists(file_name):
            return

        file = open(self.file_name, "rt")

        # load existing data + ignore header
        lines = file.readlines()[1:]
        lines = [line.rstrip() for line in lines]
        for line in lines:
            line = line.split(',')
            if len(line) != 2:
                raise Exception("Format error")
            cmd_index = int(line[0])
            cmd_text = str(line[1])
            self.store[cmd_index] = Command(cmd_index, cmd_text)

        file.close()

    def save(self) -> None:
        """
        Saves the command store to disk.
        :return: None
        """
        file = open(self.file_name, "w+")
        indexes = list(self.store.keys())
        indexes.sort()

        file.write("index,command_text\n")
        for index in indexes:
            file.write(str(index) + "," + self.store[index].text + "\n")

        file.close()

    def get_command_by_text(self, command_text: str) -> Command:
        """
        Searches for the command by the command_text.
        If the command_text does not already exist, a new command is created.
        Else, the existing command is returned.
        :param command_text: the command text to search for.
        :return: the found or created command.
        """

        # linear search for existing command_text
        for key in self.store:
            val = self.store[key]
            if val.text == command_text:
                return self.store[key]

        # not found, add new command
        new_index = len(self.store)
        if new_index in self.store:
            raise Exception("Bad store format, indexing should be sequential")
        else:
            # add new command
            cmd = Command(new_index, command_text)
            self.store[new_index] = cmd
            return cmd

    def get_command_by_index(self, index: int) -> Command:
        if index in self.store:
            return self.store[index]
        else:
            raise Exception("Invalid index")

    def get_commands_by_index_list(self, indexes: List[int]) -> List[Command]:
        result = []
        for index in indexes:
            result.append(self.get_command_by_index(index))
        return result


class ActivityStore:
    """
    Represents a file containing all known activities.

    FILE FORMAT:
    (activity_index),(activity_name),(command_index1),(command_index2),(command_indexN)
    (activity_index),(activity_name),(command_index1),(command_index2),(command_indexN)
    (activity_index),(activity_name),(command_index1),(command_index2),(command_indexN)
    """

    def __init__(self, file_name: str, command_store: CommandStore):
        """
        Attempts to load an existing activities store.
        If the store is not found, a new one is created.
        :param file_name: the file to save the activity store in.
        """
        self.file_name = file_name
        self.command_store = command_store
        self.store = {}

        if not exists(file_name):
            return

        # load activities
        file = open(file_name, "r")

        lines = file.readlines()[1:]
        for line in lines:
            cols = line.rstrip().split(",")
            if len(cols) < 2:
                raise Exception("Format error")
            activity_index = int(cols[0])
            activity_name = str(cols[1])
            command_indexes = cols[2:]
            command_indexes = [int(x) for x in command_indexes]

            commands = self.command_store.get_commands_by_index_list(command_indexes)
            self.store[activity_index] = Activity(activity_name, activity_index, commands)

        file.close()

    def save(self) -> None:
        """
        Saves the activity store to disk.
        :return: None
        """
        file = open(self.file_name, "w+")
        indexes = list(self.store.keys())
        indexes.sort()

        file.write("index,activity_name,commands(0..n)\n")
        for index in indexes:
            activity = self.store[index]
            file.write(str(activity.index) + "," + activity.name)
            for cmd in activity.commands:
                file.write("," + str(cmd.index))
            file.write("\n")

        file.close()

    def get_activity_by_index(self, index: int) -> Activity:
        if index in self.store:
            return self.store[index]
        else:
            raise Exception("Invalid index")

    def get_activities_by_index_list(self, indexes: List[int]) -> List[Activity]:
        result = []
        for index in indexes:
            result.append(self.get_activity_by_index(index))
        return result

    def new_activity(self, name: str, commands: List[Command]) -> Activity:
        new_index = len(self.store)
        if new_index in self.store:
            raise Exception("Bad store format, indexing should be sequential")
        else:
            # add new activity
            activity = Activity(name, new_index, commands)
            self.store[new_index] = activity
            return activity


class SecurityAttributeStore:
    """
    Represents a file containing all known security attributes.

    FILE_FORMAT:
    (attribute_index),(attribute_name),(activity_index1),(activity_index2),(activity_indexN)
    (attribute_index),(attribute_name),(activity_index1),(activity_index2),(activity_indexN)
    (attribute_index),(attribute_name),(activity_index1),(activity_index2),(activity_indexN)
    """

    def __init__(self, file_name: str, activity_store: ActivityStore):
        """
        Attempt to load existing attribute store.
        If the store is not found, a new one is created.
        :param file_name: the file to save the attribute store in.
        """
        self.file_name = file_name
        self.activity_store = activity_store
        self.store = {}

        if not exists(file_name):
            return

        # load attributes
        file = open(file_name, "r")

        lines = file.readlines()[1:]
        for line in lines:
            cols = line.rstrip().split(",")
            if len(cols) < 2:
                raise Exception("Format error")

            attr_index = int(cols[0])
            attr_name = str(cols[1])

            activity_indexes = cols[2:]
            activity_indexes = [int(x) for x in activity_indexes]

            activities = self.activity_store.get_activities_by_index_list(activity_indexes)
            self.store[attr_index] = SecurityAttribute(attr_name, attr_index, activities)

    def save(self) -> None:
        """
        Saves the security attributes to disk.
        :return: None
        """
        file = open(self.file_name, "w+")
        indexes = list(self.store.keys())
        indexes.sort()

        file.write("index,attribute_name,activities(0..n)\n")
        for index in indexes:
            attr = self.store[index]
            file.write(str(attr.index) + "," + attr.name)
            for activity in attr.activities:
                file.write("," + str(activity.index))
            file.write("\n")

        file.close()

    def get_attribute_by_index(self, index: int) -> SecurityAttribute:
        if index in self.store:
            return self.store[index]
        else:
            raise Exception("Attribute not found")

    def get_attribute_by_index_list(self, indexes: List[int]) -> List[SecurityAttribute]:
        result = []
        for index in indexes:
            result.append(self.get_attribute_by_index(index))
        return result

    def get_attribute_by_name(self, name: str) -> SecurityAttribute:

        # linear search
        for attr in self.store.values():
            if attr.name == name:
                return attr

        # else add
        new_index = len(self.store)
        if new_index in self.store:
            raise Exception("Bad store format, indexing should be sequential")
        else:
            # add new attribute
            attr = SecurityAttribute(name, new_index, [])
            self.store[new_index] = attr
            return attr
        pass


class Target:
    """
    A target is a set of multiple security attributes that pertain to a specific target.
    Such as 'Azure Storage', 'KeyVault' etc.
    Contains a name and a list of security attributes
    """

    def __init__(self, name, file_name: str, attribute_store: SecurityAttributeStore):
        self.name = name
        self.file_name = file_name
        self.attributes = []
        self.attribute_store = attribute_store

        if not exists(file_name):
            return

        # load attr
        file = open(file_name, "r")

        lines = file.readlines()[1:]
        for line in lines:
            attr_indexes = line.rstrip().split(",")
            if len(attr_indexes) < 1:
                raise Exception("Format error")
            attr_indexes = [int(x) for x in attr_indexes]
            self.attributes = self.attribute_store.get_attribute_by_index_list(attr_indexes)

        file.close()

    def save(self) -> None:
        """
        Saves the target to disk.

        FILE FORMAT:
        (attribute_index1),(attribute_index2),(attribute_indexN)
        :return:
        """

        file = open(self.file_name, "w+")
        indexes = [x.index for x in self.attributes]
        file.write("attribute(0..n)\n")
        first = True

        for index in indexes:
            if first:
                first = False
                file.write(str(index))
            else:
                file.write("," + str(index))

        file.close()

    def add_attribute(self, attr: SecurityAttribute) -> None:
        self.attributes.append(attr)


def debug_main() -> None:
    # Create stores
    command_store = CommandStore("commands.csv")
    activity_store = ActivityStore("activities.csv", command_store)
    attribute_store = SecurityAttributeStore("attributes.csv", activity_store)

    # Create 'Azure Storage' target
    storage_target = Target("Azure Storage", "azure-storage.csv", attribute_store)

    # Create sample activities from command
    blob_upload_activity = activity_store.new_activity("UploadToBlob", [
        command_store.get_command_by_text(
            "az storage blob upload --account-name <storage-account> --container-name <container> --name myFile.txt "
            "--file myFile.txt --auth-mode login")
    ])

    blob_list_activity = activity_store.new_activity("ListBlobs", [
        command_store.get_command_by_text(
            "az storage blob list --account-name <storage-account> --container-name <container> --output table "
            "--auth-mode login"
        )
    ])

    blob_download_activity = activity_store.new_activity("DownloadFromBlob", [
        command_store.get_command_by_text(
            "az storage blob download --account-name <storage-account> --container-name <container> --name myFile.txt "
            "--file <~/destination/path/for/file> --auth-mode login"
        )
    ])

    # Create 'Blob' attribute
    attr = attribute_store.get_attribute_by_name("Blob")

    # Add activity to attribute.
    attr.add_activity(blob_upload_activity)
    attr.add_activity(blob_list_activity)
    attr.add_activity(blob_download_activity)

    # Add attribute to target
    storage_target.add_attribute(attr)

    # Execute activity
    blob_download_activity.execute_activity()

    # Save stores
    command_store.save()
    activity_store.save()
    attribute_store.save()
    storage_target.save()


def importer():
    command_store = CommandStore("commands.csv")
    activity_store = ActivityStore("activities.csv", command_store)
    attribute_store = SecurityAttributeStore("attributes.csv", activity_store)

    target_name = input("ENTER TARGET NAME: ")
    target_file_name = convert_to_file_name(target_name) + ".csv"
    attribute_name = input("ENTER ATTRIBUTE NAME: ")
    activity_name = input("ENTER ACTIVITY NAME: ")
    print("ENTER COMMANDS: (and Ctrl-Z when done)")
    commands = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        commands.append(line)

    target = Target(target_name, target_file_name, attribute_store)
    attr = attribute_store.get_attribute_by_name(attribute_name)

    # Create sample activities from command
    activity = activity_store.new_activity(activity_name, [
        command_store.get_command_by_text(cmd) for cmd in commands
    ])

    attr.add_activity(activity)

    target.add_attribute(attr)

    # Save stores
    command_store.save()
    activity_store.save()
    attribute_store.save()
    target.save()



if __name__ == '__main__':
    debug_main()
