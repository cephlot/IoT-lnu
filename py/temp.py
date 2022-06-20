from machine import ADC
import time

adc = ADC(26)

while True:
    voltage = adc.read_u16()*(3.3/65535)
    print(voltage)
    temp = (voltage - 0.5)/0.01
    print(temp)

    time.sleep(1)
