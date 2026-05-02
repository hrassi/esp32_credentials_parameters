# example fo using config.params to get wifi credentials
# from config.txt . in this example we get wifi crdentials
# then connect to wifi, then print the clock to test if wifi is connected

import clock
import time
from wifi_connect import wifi_loop
from config.params import read, write



MyNetwork = read("MyNetwork")
MyPassword = read("MyPassword")

print(MyNetwork,MyPassword)



# # ───── 1. WAIT FOR WIFI AT STARTUP ─────
#
print("[System] Connecting to WiFi...")

while not wifi_loop(MyNetwork, MyPassword):
    time.sleep_ms(500)

print("[System] WiFi connected!")


print("time : ",clock.get_time())
print("date : ",clock.get_date())
print("date time : ",clock.get_date_time())
print("day : ",clock.get_day())




'''

# structure of the config.txt file : always 20 lines
# line1: variable name and line2: value ...and so on ... 20 lines means 10 variables

MyNetwork
Rassi Net3
MyPassword
Holyshit
slot3_empty
-
slot4_empty
-
slot5_empty
-
slot6_empty
-
slot7_empty
-
slot8_empty
-
slot9_empty
-
slot10_empty
-



# read a value from the config.txt file:
wifi_ssid     = read("wifi_ssid")      # read by name
wifi_password = read("wifi_password")
mqtt_broker   = read(3)                # read by slot number
device_name   = read("device_name")
interval      = int(read(5))           # convert to int



# write a value back at runtime
write("device_name", "esp32-node-01")
write(5, 30)

'''