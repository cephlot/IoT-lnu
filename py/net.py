import network, socket, time, secrets

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

def http_get(url ="detectportal.firefox.com"):
    """Sends a HTTP GET request on port 80 to the specified url

    :param url: url to send request to, defaults to "detectportal.firefox.com"
    :type url: str, optional
    """

    addr = socket.getaddrinfo(url, 80)[0][4]
    print(addr)

    # Create a new socket and connect to addr
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(addr)

    # Set timeout
    client.settimeout(3.0)

    # Send HTTP request and recv response
    client.send("GET / HTTP/1.1\r\nHost: %s\r\n\r\n"%(url))
    print(client.recv(1024))

    # Close socket
    client.close()

# Connect to WiFi specified in 'secrets.py'
do_connect()

# Sends HTTP GET request to url
http_get()
