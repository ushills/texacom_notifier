# Code for Texecom Veritas Alarm communicator inteface
# using esp8266 - Nodemcu Development Kit to send alarm
# communications to IFTTT to trigger external responses


# Output from communicator ports is 12V+ and a voltage
# divider is required to reduce to 3.3V.
# use 10k(R1) and 3.3k(R2) to step down 12-13v > 3.3V

# Communicator Interface Channels
# Channel 3 = Intruder
# Channel 4 = Set/Unset
# Channel 8 = 2nd Intruder (Sequentally confirmed alarm)
# R/R can be used for remote reset but not currently implemented
# Pins are high by default and therefore a value of 0 indicates
# an alarm state

from machine import Pin, Signal
import network
import usocket as socket

# global variables
WEBHOOK_KEY = "{{webhook_key}}"
WEBHOOK_EVENT = "{{webhook_event}}"
BASE_URL = "https://maker.ifttt.com"
SSID = "{SSID name}"
SSID_PASSWORD = "{SSID password}"

# define inputs
# INTRUDER_PIN = D1 (GPIO5)
INTRUDER_PIN = Pin(5, Pin.IN)
# SET_UNSET_PIN = D2 (GPIO4)
SET_UNSET_PIN = Pin(4, Pin.IN)
# SECOND_INTRUDER_PIN = D3 (GPIO0)
SECOND_INTRUDER_PIN = Pin(0, Pin.IN)

# define outputs
# esp LED
WIFI_LED_PIN = Pin(16, Pin.OUT)
wifi_LED = Signal(WIFI_LED_PIN, invert=True)


# define signals
intruder_signal = Signal(INTRUDER_PIN, invert=True)
set_unset_signal = Signal(SET_UNSET_PIN, invert=True)
second_intruder_signal = Signal(SECOND_INTRUDER_PIN, invert=True)


class OutputManager:
    def __init__(self):
        self.output_is_active = False
        self.command1 = None
        self.command2 = None

    def check_output(self, output_value):
        update_output = output_value != self.output_is_active
        if update_output:
            if output_value is True:
                self.trigger_command()
            else:
                self.cease_command()
        self.output_is_active = output_value

    def trigger_command(self):
        print("{} command 1 triggered".format(self.command1))
        return "command triggered"

    def cease_command(self):
        if self.command2 is not None:
            print("{} command2 triggered".format(self.command2))
            return "command2 triggered"
        else:
            print("{} ceased".format(self.command1))
            return "cease triggered"


def create_url(action):
    url = (
        BASE_URL
        + "/trigger/"
        + WEBHOOK_EVENT
        + "/with/key/"
        + WEBHOOK_KEY
        + "?value1="
        + action
    )
    return url


def wifi_connected():
    if not wlan.isconnected():
        wifi_LED.off()


def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect("SSID", "SSIDPASSWORD")
        while not wlan.isconnected():
            pass
    print("network config:", wlan.ifconfig())
    wifi_LED.on()
    return wlan


def send_webhook(url):
    full_url = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(url).encode()
    addr = socket.getaddrinfo(BASE_URL, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(full_url)
    # may not need to receive data, check if webhook works without and delete
    # data = s.recv(1000)
    s.close()
    return True


if __name__ == "__main__":
    # initialise variables
    intruder_signal_value = intruder_signal.value()
    set_unset_signal_value = set_unset_signal.value()
    second_intruder_signal_value = second_intruder_signal.value()
    alarm_state = None
    set_state = None
    second_intruder_state = None

    # connect to the network
    wifi_connect()

    # main loop poll all signals if wifi is connected else re-connect network
    while True:
        if wifi_connected:
            poll_all_signals()
        else:
            wifi_connect()
