import time
import random
from machine import Pin
from neopixel import NeoPixel

btn = Pin(0, Pin.IN, Pin.PULL_UP)
neo = NeoPixel(Pin(33), 1)

press_count = 0
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

print("Starting Neopixel Flashing")

while True:
    if btn.value() == 0:
        press_count += 1
        print(f"Button Pressed! Total Presses: {press_count}")
        time.sleep(0.2)

        if press_count % 5 == 0:
            color = random.choice(colors)
            print(f"Changing Neopixel Color to: {color}")
            neo[0] = color
            neo.write()
        else:
            print("No color change, LED is off.")
            neo[0] = (0, 0, 0)
            neo.write()

    else:
        neo[0] = (0, 0, 0)
        neo.write()

    time.sleep(0.1)
