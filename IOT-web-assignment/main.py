import network
import socket
import dht
import machine
import ssd1306  # OLED library

# WiFi Configuration
SSID = "StormFiber-4cd8"
PASSWORD = "03326552418"

# Initialize WiFi in Station Mode
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

while not wifi.isconnected():
    pass  # Wait for connection

print("Connected! IP Address:", wifi.ifconfig()[0])

# Initialize DHT11 Sensor
dht_pin = machine.Pin(4)  # GPIO4
dht_sensor = dht.DHT11(dht_pin)

# Initialize OLED Display (SSD1306)
i2c = machine.SoftI2C(scl=machine.Pin(9), sda=machine.Pin(8))  
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Initialize RGB LED (Built-in NeoPixel)
from neopixel import NeoPixel  # Import NeoPixel library

rgb_pin = machine.Pin(48, machine.Pin.OUT)  # Change pin if needed
rgb_led = NeoPixel(rgb_pin, 1)  # Only 1 LED on ESP32
  

# Function to Set RGB Color
def set_rgb_color(r, g, b):
    rgb_led[0] = (r, g, b)
    rgb_led.write()


# Function to Read Temperature & Humidity
def get_sensor_data():
    dht_sensor.measure()
    temp = dht_sensor.temperature()
    hum = dht_sensor.humidity()
    return temp, hum

# HTML Web Page
def generate_webpage(temp, hum):
    return """ 
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Web Server</title>
        <style>
            body { font-family: Arial; text-align: center; }
            .container { width: 80%%; margin: auto; }
            input { padding: 10px; font-size: 16px; }
            button { padding: 10px; font-size: 18px; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 RGB LED & Sensor Web Server</h1>
            <h2>Temperature: """ + str(temp) + """°C</h2>
            <h2>Humidity: """ + str(hum) + """%</h2>

            <h3>Set RGB Color</h3>
            <form action="/" method="GET">
                <input type="number" name="r" placeholder="Red (0-255)">
                <input type="number" name="g" placeholder="Green (0-255)">
                <input type="number" name="b" placeholder="Blue (0-255)">
                <button type="submit">Set Color</button>
            </form>
        </div>
    </body>
    </html>
    """

# Start Web Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 80))
server.listen(5)

print("Web Server Started! Access it via browser.")

while True:
    conn, addr = server.accept()
    print("Client connected from", addr)
    
    request = conn.recv(1024).decode()
    
    # Parse RGB Values
    if "GET /?" in request:
        try:
            params = request.split(" ")[1].split("?")[1].split("&")
            r = int(params[0].split("=")[1])
            g = int(params[1].split("=")[1])
            b = int(params[2].split("=")[1])
            set_rgb_color(r, g, b)
            oled.fill(0)
            oled.text("Color: R{} G{} B{}".format(r, g, b), 0, 20)
            oled.show()
        except:
            pass
    
    # Get Sensor Data
    temp, hum = get_sensor_data()

    # Send Webpage Response
    response = generate_webpage(temp, hum)
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response)
    conn.close()