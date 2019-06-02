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


"""The Notifier class checks the inputs from a signal and depending on the 
input triggers certain external actions, in this case triggering a webhook
using IFTTT.

The class has the following methods for direct use:

    check_signal(signal_input) - checks the signal and triggers the webhook 
        if state has changed.
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
        update_signal = signal_value != self.signal_is_active
        if update_signal is True:
            if signal_value is True:
                self.signal_is_active = True
                return self.trigger_action1()
            else:
                self.signal_is_active = False
                return self.trigger_action2_or_cease()

    def trigger_action1(self):
        return self.send_webhook(self.action1)

    def trigger_action2_or_cease(self):
        print("\naction2 = ", self.action2)
        if self.action2 is None:
            return self.action1 + " ceased"

        else:
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
        full_url = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(
            self.create_url(action)
        ).encode()
        addr = socket.getaddrinfo(BASE_URL, 80)[0][-1]
        s = socket.socket()
        s.connect(addr)
        s.send(full_url)
        # may not need to receive data, check if webhook works without and delete
        # data = s.recv(1000)
        s.close()
        print("webhook sent")
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


if __name__ == "__main__":
    # initialise intruder class
    intruder = Notifier()
    intruder.set_action1("intruder detected")

    # initialise second intruder class
    second_intruder = Notifier()
    second_intruder.set_action1("second intruder detected")

    # initialise set_unset class
    set_unset = Notifier()
    set_unset.set_action1("alarm set")
    set_unset.set_action2("alarm unset")

    # connect to the network
    wifi_connect()

    # main loop poll all signals if wifi is connected else re-connect network
    while True:
        if wifi_connected:
            intruder.check_signal(intruder_signal)
            second_intruder.check_signal(second_intruder_signal)
            set_unset.check_signal(set_unset_signal)
        else:
            wifi_connect()
