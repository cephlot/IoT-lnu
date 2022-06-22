from machine import ADC
import network, socket, time, secrets, ubinascii, machine
from umqttsimple import MQTTClient

def do_connect():
    """Connects to a WiFi network with specified SSID
    """
    SSID=secrets.SSID # Network SSID
    KEY=secrets.KEY  # Network key

    # Init wlan module and connect to network
    print("Trying to connect. Note this may take a while...")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, KEY)

    # We should have a valid IP now via DHCP
    print("Wi-Fi Connected ", wlan.ifconfig())

def connect_mqtt():
    """Connects to an MQTT broker

    :return: MQTT client class
    :rtype: MQTTClient
    """    
    global client_id, mqtt_server

    print(f'id:{client_id}, mqtt:{mqtt_server}')

    client = MQTTClient(client_id, mqtt_server, port=1883, keepalive=30)
    client.connect()

    print(f'Connected to {mqtt_server} MQTT broker')

    return client

def restart_and_reconnect():
    """Callback used when connection to MQTT broker fails
    """    
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    machine.reset()

# Connect to WiFi specified in 'secrets.py'
do_connect()

# Create an ADC object
adc = ADC(26)

# Define conversion between 16-bit ADC to Volts
CONV = 3.3/65535.0

# Define MQTT topic
TOPIC = b'rp2040/mcp9700/temperature'

# Define MQTT server and id
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = secrets.MQTT

# Define MQTT control
last_message = 0
message_interval = 5

# Create MQTT client connection
try:
  client = connect_mqtt()
except OSError as e:
  restart_and_reconnect()

while True:
    sum = 0

    # Collect samples
    for i in range(0,10):
        voltage = adc.read_u16()*CONV
        sum += (voltage - 0.5)/0.01

    # Take the mean of the samples
    temp = sum/10.0
    print(temp)

    if (time.time() - last_message) > message_interval:
        client.publish(TOPIC, (b'{0:3.1f},'.format(temp)))
        last_message = time.time()

    time.sleep(10)
