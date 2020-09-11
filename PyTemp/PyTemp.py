#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys
import matplotlib.pyplot as plt
from matplotlib.pyplot import switch_backend
from test.support import temp_cwd

# Configuration
FAN_PIN = 4  # BCM pin used to drive transistor's base
WAIT_TIME = 2  # [s] Time to wait between each refresh
FAN_MIN = 25  # [%] Fan minimum speed.
PWM_FREQ = 30  # [Hz] Change this value if fan has strange behavior
START_DELAY = 2  # [s] Time to wait while starting the fan from a full stop

# Configurable temperature and fan speed steps
tempSteps = [50, 70]  # [°C]
speedSteps = [0, 100]  # [%]

# Fan speed will change only of the difference of temperature is higher than hysteresis
hyst = 1

i = 0
cpuTemp = 0
fanSpeed = 0
cpuTempOld = 0
fanSpeedOld = 0
tempHistory = []
fanSpeedHistory = []


def measureTemp():
    # Read CPU temperature
    cpuTempFile = open("/sys/class/thermal/thermal_zone0/temp", "r")
    cpuTemp = float(cpuTempFile.read()) / 1000
    cpuTempFile.close()
    print("CPU temperature: " + str(cpuTemp))
    tempHistory.append(cpuTemp)


def measureFanSpeed():
    cpuTemp = tempHistory[len(tempHistory)]
    # Calculate desired fan speed
    if(abs(cpuTemp - cpuTempOld) > hyst):
        # Below first value, fan will run at min speed.
        if(cpuTemp < tempSteps[0]):
            fanSpeed = speedSteps[0]
        # Above last value, fan will run at max speed
        elif(cpuTemp >= tempSteps[len(tempSteps) - 1]):
            fanSpeed = speedSteps[len(tempSteps) - 1]
        # If temperature is between 2 steps, fan speed is calculated by linear interpolation
        else:
            for i in range(0, len(tempSteps) - 1):
                if((cpuTemp >= tempSteps[i]) and (cpuTemp < tempSteps[i + 1])):
                    fanSpeed = round((speedSteps[i + 1] - speedSteps[i])
                                     / (tempSteps[i + 1] - tempSteps[i])
                                     * (cpuTemp - tempSteps[i])
                                     + speedSteps[i], 1)

        if(fanSpeed != fanSpeedOld):
            if (fanSpeed != fanSpeedOld and (fanSpeed >= FAN_MIN or fanSpeed == 0)):
                if(fanSpeedOld == 0):
                    fanSpeed = 100
                    time.sleep(START_DELAY)
                # [DEBUG]: Pritn the fan speed for debug
                # print('The Fan Speed is: ' + fanSpeed + '\n')
                fanSpeedOld = fanSpeed
        cpuTempOld = cpuTemp


try:
    while True:
        measureTemp()
        measureFanSpeed()
        # Wait until next refresh
        time.sleep(WAIT_TIME)

except KeyboardInterrupt:
    choice = input(
        'Temperature Measuring Sample Finished... \n' +
        'Did you want to save: \n' +
        '\t1 --> A CPU Temperaure Graph\n' +
        '\t2 --> A Fan Speed Graph' +
        '\t3 --> None of them. Exit.'
    )

    if(choice == 1):

        plt.plot(tempHistory, color="red")
        plt.title("Temperature")
        plt.savefig("./TemperatureGraph.png")
    elif(choice == 2):
        plt.plot(fanSpeedHistory, color="red")
        plt.title("Fan Speed")
        plt.savefig("./FanSpeedGraph.png")
    elif(choice == 3):
        pass
