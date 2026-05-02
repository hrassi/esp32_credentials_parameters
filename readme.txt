# ESP32 Params System — Usage Guide

## What this is
A reusable MicroPython module for ESP32 that lets you store and edit
project parameters (wifi credentials, settings, variables...) in a
simple text file, editable from your phone via a web interface.

---

## File structure to deploy on every ESP32 project
```
boot.py
main.py
/config/
    __init__.py
    params.py
    params_server.py
    config.txt
```

---

## How to configure a new project

1. Open config/config.txt
2. Replace slot names with your variable names, leave the value on the line below as - for now:

```
wifi_ssid
-
wifi_password
-
mqtt_broker
-
device_name
-
slot5_empty        <-- unused slots stay like this
-
...
```

3. Keep a comment at the top of your main.py reminding you what each slot is:
```python
# slot 1 = wifi_ssid
# slot 2 = wifi_password
# slot 3 = mqtt_broker
# slot 4 = device_name
```

---

## How to enter config mode and fill in values

1. Power on the ESP32 (or press the RESET button)
2. The onboard LED blinks fast for 2 seconds
3. During those 2 seconds, press and hold the BOOT button (GPIO0)
4. ESP32 creates a WiFi access point:
   - SSID     : sam
   - Password : 12345678   (min 8 chars required by WPA2)
5. Connect your phone to that WiFi network
6. Open browser and go to: http://192.168.4.1
7. You will see a dark form with all your named slots as labels
8. Fill in the values and tap "Save & Reboot"
9. ESP32 saves the values to config.txt and restarts automatically
10. On restart the LED blinks, you do NOT press BOOT, main.py runs normally

Note: empty slots (slot_empty / value -) are hidden in the web UI.
Note: if config.txt does not exist at all, ESP32 goes to config mode automatically on first boot.

---

## How to read and write values in main.py

# IMPORTANT : 
#        a 20 lines config.txt file must be present in the config folder
#        and all the variables must be declared in config.txt file in conception mode
#        each unused empty pair of line must contain :
#
#                                          slot9_empty
#                                          -
#                                          slot10_empty
#                                          -


```python
from config.params import read, write

# read by name (recommended, more readable)
ssid = read("wifi_ssid")

# read by slot number
broker = read(3)

# all values are strings, convert as needed
interval = int(read("update_interval"))
flag = read("active") == "true"

# write a value back at runtime
write("device_name", "esp32-node-01")
write(4, "new_value")
```

---

## config.txt format rules
- Always exactly 20 lines (10 slots)
- Odd lines  = variable name (label)
- Even lines = variable value (what you edit from the phone)
- Unused slots: name ends with _empty, value is -
- Everything is stored as plain string

---

## AP credentials (hardcoded in params_server.py)
- SSID     : sam
- Password : 12345678
- These never change across projects, you always know how to connect
- To change them edit AP_SSID and AP_PASS at the top of params_server.py

---

## Memory note
params_server.py (the heavy part: web server + HTML) is ONLY loaded
in config mode. In normal run mode only params.py is in memory,
which is tiny (just read and write functions).