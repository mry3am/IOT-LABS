import network
import socket
import dht
import machine
import ssd1306  # OLED library
from neopixel import NeoPixel  # Import NeoPixel library

# WiFi Configuration
SSID = "Hadia"
PASSWORD = "8777hadia"

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

# Function to Update OLED Display
# Global variable to track last update mode
# Global variable to track last update mode
last_update_mode = "sensor"  # Default mode (Shows Temp & Hum)

def update_oled(temp, hum, r, g, b, mode=None):
    global last_update_mode
    
    oled.fill(0)  # Clear the screen

    if mode is None:
        mode = last_update_mode  # Keep the last mode if not explicitly set
    
    print(f"Updating OLED - Mode: {mode}")  # ✅ Debug print
    print(f"Temp: {temp}, Hum: {hum}, R: {r}, G: {g}, B: {b}")  # ✅ Debug print
    
    if mode == "sensor":  # Show temperature and humidity
        oled.text("Temp: {}C".format(temp), 0, 10)
        oled.text("Hum: {}%".format(hum), 0, 20)
        last_update_mode = "sensor"  # Update mode tracker
    
    elif mode == "rgb":  # Show RGB values
        oled.text("Color:", 0, 10)
        oled.text("R:{} G:{} B:{}".format(r, g, b), 0, 30)
        last_update_mode = "rgb"  # Update mode tracker
    
    oled.show()  # Display the updated text

# HTML Web Page
def generate_webpage(temp, hum):
    return """ 
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Sensor & RGB Control</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #121212;
                color: #ffffff;
                text-align: center;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 80%%;
                margin: auto;
                padding: 20px;
            }
            h1 {
                font-size: 28px;
                color: #ff9800;
                text-transform: uppercase;
            }
            .sensor-data {
                font-size: 22px;
                padding: 10px;
                background: linear-gradient(45deg, #ff9800, #ff5722);
                display: inline-block;
                border-radius: 10px;
                box-shadow: 2px 2px 10px rgba(255, 87, 34, 0.5);
                margin-bottom: 20px;
            }
            .form-container {
                background: #222;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 2px 2px 15px rgba(255, 255, 255, 0.1);
                display: inline-block;
            }
            input {
                width: 80px;
                padding: 8px;
                font-size: 18px;
                border-radius: 5px;
                border: none;
                text-align: center;
                background: #444;
                color: #fff;
                margin: 5px;
            }
            button {
                background: linear-gradient(45deg, #ff5722, #ff9800);
                color: white;
                font-size: 18px;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                margin-top: 10px;
                transition: 0.3s;
            }
            button:hover {
                transform: scale(1.1);
                background: linear-gradient(45deg, #ff9800, #ff5722);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 Sensor & RGB Control</h1>
            <div class="sensor-data">
                <p>Temperature: """ + str(temp) + """*C</p>
                <p>Humidity: """ + str(hum) + """%</p>
            </div>

            <h3>Set RGB Color</h3>
            <div class="form-container">
                <form action="/" method="GET">
                    <input type="number" name="r" placeholder="Red (0-255)">
                    <input type="number" name="g" placeholder="Green (0-255)">
                    <input type="number" name="b" placeholder="Blue (0-255)">
                    <br>
                    <button type="submit">Change Color</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

# Start Web Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 80))
server.listen(5)

print("Web Server Started! Access it via browser.")

# Default RGB Values
r, g, b = 0, 0, 0

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
            update_oled(0, 0, r, g, b, mode="rgb")
        except Exception as e:
            print("Error parsing RGB values:", e)

    # Get Sensor Data
    temp, hum = get_sensor_data()

    # **Update OLED Display**
    update_oled(temp, hum, r, g, b)

    # Send Webpage Response
    response = generate_webpage(temp, hum)
    conn.send("HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + response)
    conn.close()