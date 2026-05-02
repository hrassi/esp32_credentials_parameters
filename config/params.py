# params.py is used to read or write variables and credentials to config.txt file
# usage: from config.params import read, write
#        ssid = read("wifi_ssid") # read the value of the wifi_ssid variable inside the config.txt
#        write("counter", "10")   # give to the variable called counter the value 10
#        all values are strings, to convert : my_counter = int(read("counter"))
#
### config.txt format rules:
#        Always exactly 20 lines (10 slots)
#        each 2 line for one variable ( first line the variable name, second line its value )
#        Unused slot(pair of lines): first line = _empty, second line = -
#        Everything is stored as plain string
#
# IMPORTANT : 
#        a 20 lines config.txt file must be present in the config folder
#        and all the variables must be declared in config.txt file in conception mode
#        each unused empty pair of line must contain :
#
#                                          slot9_empty
#                                          -
#                                          slot10_empty
#                                          -
#


CONFIG_FILE = "/config/config.txt"
TOTAL_SLOTS = 10


def _load():
    lines = []
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                lines.append(line.rstrip("\n"))
    except OSError:
        pass
    return lines


def _save(lines):
    with open(CONFIG_FILE, "w") as f:
        for line in lines:
            f.write(line + "\n")


def _slot_to_index(slot_or_name):
    lines = _load()
    if isinstance(slot_or_name, int):
        if 1 <= slot_or_name <= TOTAL_SLOTS:
            return (slot_or_name - 1) * 2, lines
        return None, lines
    for i in range(0, len(lines), 2):
        if lines[i] == slot_or_name:
            return i, lines
    return None, lines


def read(slot_or_name):
    idx, lines = _slot_to_index(slot_or_name)
    if idx is None or idx + 1 >= len(lines):
        return None
    return lines[idx + 1]


def write(slot_or_name, value):
    idx, lines = _slot_to_index(slot_or_name)
    if idx is None or idx + 1 >= len(lines):
        return False
    lines[idx + 1] = str(value)
    _save(lines)
    return True
