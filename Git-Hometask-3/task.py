import machine
import time
import dht
import ssd1306

# Initialize I2C for OLED display on ESP32 (change pins if needed)
i2c = machine.I2C(0, scl=machine.Pin(9), sda=machine.Pin(8))  # Change pins if necessary
oled_width = 128  # Width of the OLED screen
oled_height = 64  # Height of the OLED screen
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Initialize DHT sensor on GPIO4
sensor = dht.DHT11(machine.Pin(4))  # Data pin is GPIO4

# Function to display temperature and humidity with symbols
def display_data(temp, humidity):
    oled.fill(0)  # Clear the display
    # Display temperature with a simple symbol
    oled.text("Temperature: {}C °".format(temp), 0, 10)  # Using degree symbol for temperature
    # Display humidity with a simple symbol
    oled.text("Humidity: {}% ~".format(humidity), 0, 30)  # Using tilde as a humidity symbol
    oled.show()  # Update the display

# Task 1: Display temperature and humidity on OLED
while True:
    try:
        sensor.measure()  # Take a measurement
        temp = sensor.temperature()  # Get temperature
        humidity = sensor.humidity()  # Get humidity
        print("Temperature:", temp, "C")
        print("Humidity:", humidity, "%")
        
        # Display data on OLED
        display_data(temp, humidity)
        
    except OSError as e:
        print("Error reading sensor:", e)

    time.sleep(2)  # Delay before the next reading


