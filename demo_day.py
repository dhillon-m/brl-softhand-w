##############################
# Import necessary libraries #
##############################

import serial
import serial.tools.list_ports
import time
import numpy as np

import soft_wrist_lib as swl



################################
# Setup wrist and hand control #
################################

# List available serial ports
ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device)

# Open serial port
ser = serial.Serial('COM4', baudrate=1000000, timeout=0.1)



###############
# Test Script #
###############
swl.close_hand(ser)
swl.wait_for_servo(ser, servo_ids=[2, 3])
swl.home_hand(ser)

# Close the serial port
ser.close()