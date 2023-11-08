# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import busio
import digitalio
import board
import Adafruit_CircuitPython_MCP3xxx.adafruit_mcp3xxx.mcp3008 as MCP
from Adafruit_CircuitPython_MCP3xxx.adafruit_mcp3xxx.analog_in import AnalogIn
from time import sleep

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

while True:
    #print("Raw ADC Value: ", chan.value)
    print("ADC Voltage: " + str(chan.voltage) + "V")
    sleep(1)