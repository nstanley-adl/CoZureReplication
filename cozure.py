from os.path import exists


class Command:
    """
    Smallest building block, representing a single command.
    Contains a unique index, and command text.
    The text may contain parameters, these are substituted at runtime.
    """

    def __init__(self, index, text):
        self.index = index
        self.text = text


class Activity:
    """
    An ordered subset of commands which are combined to achieve an objective.
    Contains a name, an index, and list of commands.
    An activity must be meaningful, commands by not arbitrarily form an activity.
    """

    def __init__(self, name, index, commands):
        self.name = name
        self.index = index
        self.commands = commands


class SecurityAttribute:
    """
    A security attribute is an ordered set of multiple activities.
    Contains a name, an index, and list of activities.
    """

    def __init__(self, name, index, activities):
        self.name = name
        self.index = index
        self.activities = activities

    def add_activity(self, activity):
        self.activities.append(activity)


class Target:
    """
    A target is a set of multiple security attributes that pertain to a specific target.
    Such as 'Azure Storage', 'KeyVault' etc.
    Contains a name and a list of security attributes
    """

    def __init__(self, name, file_name, attribute_store):
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

    def save(self):
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

    def add_attribute(self, attr):
        self.attributes.append(attr)


class CommandStore:
    """
    Represents a file containing all commands.
    Use a command store to get and fetch commands.

    FILE FORMAT:
    (command_index),(command_text)
    (command_index),(command_text)
    (command_index),(command_text)
    """

    def __init__(self, file_name):
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

    def save(self):
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

    def get_command_by_text(self, command_text):
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

    def get_command_by_index(self, index):
        if index in self.store:
            return self.store[index]
        else:
            raise Exception("Invalid index")

    def get_commands_by_index_list(self, indexes):
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

    def __init__(self, file_name, command_store):
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

    def save(self):
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

    def get_activity_by_index(self, index):
        if index in self.store:
            return self.store[index]
        else:
            raise Exception("Invalid index")

    def get_activities_by_index_list(self, indexes):
        result = []
        for index in indexes:
            result.append(self.get_activity_by_index(index))
        return result

    def new_activity(self, name, commands):
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

    def __init__(self, file_name, activity_store):
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

    def save(self):
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

    def get_attribute_by_index(self, index):
        if index in self.store:
            return self.store[index]
        else:
            raise Exception("Attribute not found")

    def get_attribute_by_index_list(self, indexes):
        result = []
        for index in indexes:
            result.append(self.get_attribute_by_index(index))
        return result

    def get_attribute_by_name(self, name):

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


def debug_execute_target(target):
    print(f"Executing '{target.name}'...")

    # iterate through each command sequentially.
    for security_attribute in target.security_attributes:
        print(f"# attribute: {security_attribute.name}")
        for activity in security_attribute.activities:
            print(f"# activity: {activity.name}")
            for command in activity.commands:
                print(f"> {command}")


if __name__ == '__main__':
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

    # # Add attribute to target
    storage_target.add_attribute(attr)

    # Save stores
    command_store.save()
    activity_store.save()
    attribute_store.save()
    storage_target.save()
