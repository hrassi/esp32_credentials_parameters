# this boot.py start fast blink the onboard led for 2 sec
# during theses 2 sec if boot buttton is pushed or if the file
# /config/config.txt does not exist it launch the params_server.py
# and enter thru phone in config mode . once the variables and credentials
# are entered and saved , esp will boot aagain ... this time if boot is not pushed
# during first 2 sec the main.py will be launched


import machine
import time
import os

CONFIG_FILE = "/config/config.txt"
BOOT_PIN = 0
LED_PIN = 2
TRIGGER_WINDOW = 2000


def _config_file_exists():
    try:
        os.stat(CONFIG_FILE)
        return True
    except OSError:
        return False


def _blink_and_check():
    boot_btn = machine.Pin(BOOT_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
    led = machine.Pin(LED_PIN, machine.Pin.OUT)

    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < TRIGGER_WINDOW:
        led.value(not led.value())
        time.sleep_ms(100)
        if boot_btn.value() == 0:
            led.value(1)
            return True

    led.value(0)
    return False


config_mode = False

if not _config_file_exists():
    print("config.txt not found — entering config mode")
    config_mode = True
elif _blink_and_check():
    print("BOOT button pressed — entering config mode")
    config_mode = True
else:
    print("Normal boot — starting main.py")

if config_mode:
    from config.params_server import start_config_mode
    start_config_mode()
