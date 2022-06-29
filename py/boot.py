from machine import ADC
import network, socket, time, secrets, ubinascii, machine
from umqttsimple import MQTTClient

def connect_wifi():
    """Connects to a WiFi network with specified SSID

    :return: WLAN object
    :rtype: WLAN object
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

    return wlan

def disconnect_wifi(wlan):
    """Disconnects to the currently connected WiFi network and disables the WLAN
    module.

    :param wlan: WLAN object
    :type wlan: WLAN object
    """
    wlan.disconnect()
    wlan.active(False)

    print("Wi-Fi Disconnected")

def connect_mqtt():
    """Connects to an MQTT broker

    :return: MQTT client class
    :rtype: MQTTClient
    """
    global client_id, mqtt_server

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

# Create an ADC object
adc = ADC(26)

# Define conversion between 16-bit ADC to Volts
CONV = 3.3/65535.0

# Define MQTT topic
TOPIC = b'rp2040/mcp9700/temperature'

# Define MQTT server and id
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = secrets.MQTT

while True:
    # Connect to WiFi specified in 'secrets.py'
    wlan = connect_wifi()

    # Create MQTT client connection
    try:
      client = connect_mqtt()
    except OSError as e:
      restart_and_reconnect()

    sum = 0

    # Collect samples
    for i in range(0,100):
        voltage = adc.read_u16()*CONV
        sum += (voltage - 0.5)/0.01

    # Take the mean of the samples
    temp = sum/100.0
    print(temp)

    try:
        # Publish the temperature measurement to the MQTT server
        client.publish(TOPIC, (b'{0:3.1f}'.format(temp)))
    except OSError as e:
        # Reset the MCU if error occurs
        restart_and_reconnect()

    # Turn off WiFi module
    disconnect_wifi(wlan)

    # Sleep for 15 minutes.
    time.sleep(15*60)
