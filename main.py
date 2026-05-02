# By Houssam Rassi
# example fo using config.params
# example of a counter that remember its count after reboot

from config.params import read, write
import time

my_name = read("my_name") # read from config.txt the value of the variable my_name
x = read("x")
y = read("y")

counter = int(read("counter")) # convert string to int


print("my_name :",my_name)
print("x :",x)
print("y :",y)
print("counter :",counter)

while True:
    
    counter = int(read("counter"))
    print("my_name :",my_name)
    print("x :",x)
    print("y :",y)
    print("counter :",counter)

    
    time.sleep (1)
    # write a value back at runtime
    write("counter", counter+1)


