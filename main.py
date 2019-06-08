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
import time
import config

# global variables contained in a seperate config.py file
WEBHOOK_KEY = config.WEBHOOK_KEY
WEBHOOK_EVENT = config.WEBHOOK_EVENT
BASE_URL = config.BASE_URL
SSID = config.SSID
SSID_PASSWORD = config.SSID_PASSWORD

# create network class
wlan = network.WLAN(network.STA_IF)


# define inputs
# INTRUDER_PIN = D1 (GPIO5)
INTRUDER_PIN = Pin(5, Pin.IN, Pin.PULL_UP)
# SET_UNSET_PIN = D2 (GPIO4)
SET_UNSET_PIN = Pin(4, Pin.IN, Pin.PULL_UP)
# SECOND_INTRUDER_PIN = D4 (GPIO2)
SECOND_INTRUDER_PIN = Pin(2, Pin.IN, Pin.PULL_UP)

# define outputs
# esp LED
WIFI_LED_PIN = Pin(16, Pin.OUT)
wifi_LED = Signal(WIFI_LED_PIN, invert=True)

# define signals
intruder_signal = Signal(INTRUDER_PIN, invert=True)
set_unset_signal = Signal(SET_UNSET_PIN, invert=True)
second_intruder_signal = Signal(SECOND_INTRUDER_PIN, invert=True)


"""The Notifier class checks the inputs from a signal and depending on the
input triggers certain external actions, in this case triggering a webhook
using IFTTT.

The class has the following methods for direct use:

    check_signal(signal_input) - checks the signal and triggers the webhook
        if the signal state has changed.
    set_action1(str) - sets the action(value1) to be sent with the webhook.
    set_action2(str) - sets the action(value2) to be sent with the webhook.

The following methods are exposed but are not intended for direct use but
are available for testing purposes:

    create_url(str) - creates a url in the format required by IFTTT to
        trigger the webhook.
    send_webhook(str) - creates the full url required for Micropython usocket,
        from create_url, creates a socket connection and sends the webhook.

"""


class Notifier:
    def __init__(self):
        self.signal_is_active = False
        self.action1 = None
        self.action2 = None

    def check_signal(self, signal_value):
        if signal_value == 1:
            signal_value = True
        else:
            signal_value = False
        update_signal = signal_value != self.signal_is_active
        if update_signal is True:
            if signal_value is True:
                self.signal_is_active = True
                return self.trigger_action1()
            else:
                self.signal_is_active = False
                return self.trigger_action2_or_cease()

    def trigger_action1(self):
        print("Signal detected...", self.action1)
        return self.send_webhook(self.action1)

    def trigger_action2_or_cease(self):
        if self.action2 is None:
            print("Signal ceased...", self.action1)
            return self.action1 + " ceased"
        else:
            print("Signal removed...", self.action2)
            return self.send_webhook(self.action2)

    def create_url(self, action):
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

    def send_webhook(self, action):
        print("Sending webhook for...", action)
        url = self.create_url(action)
        _, _, host, path = url.split("/", 3)
        full_url = "GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n".format(path, host).encode()
        addr = socket.getaddrinfo(host, 80)[0][-1]
        print("Establishing socket connection...")
        s = socket.socket()
        s.connect(addr)
        print("Sending webhook...")
        s.send(full_url)
        while True:
            data = s.recv(100)
            if data:
                print(str(data, "utf8"), end="")
            else:
                break
        s.close()
        time.sleep(10)
        print("Webhook sent")
        return full_url

    def set_action1(self, action):
        self.action1 = action
        return self.action1

    def set_action2(self, action):
        self.action2 = action
        return self.action2


def wifi_connected():
    if not wlan.isconnected():
        wifi_LED.off()
        return False
    else:
        return True


def wifi_connect():
    print("turning WiFi on...")
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...", SSID)
        wlan.connect(SSID, SSID_PASSWORD)
        while not wlan.isconnected():
            pass
    print("connected to network", SSID)
    print("network config:", wlan.ifconfig())
    wifi_LED.on()
    return wlan


if __name__ == "__main__":
    print("Initialising.....")
    # initialise intruder class
    intruder = Notifier()
    intruder.set_action1("INTRUDER+DETECTED")

    # initialise second intruder class
    second_intruder = Notifier()
    second_intruder.set_action1("SECOND+INTRUDER+DETECTED")

    # initialise set_unset class
    set_unset = Notifier()
    set_unset.set_action1("Alarm+unset")
    set_unset.set_action2("Alarm+set")

    # connect to the network
    wifi_connect()

    # main loop poll all signals if wifi is connected else re-connect network
    print("Running main routine...")
    while True:
        if wifi_connected():
            intruder.check_signal(intruder_signal.value())
            second_intruder.check_signal(second_intruder_signal.value())
            set_unset.check_signal(set_unset_signal.value())
        else:
            print("Network connection failed, trying to reconnect...")
            wifi_connect()
