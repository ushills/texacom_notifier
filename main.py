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
WEBHOOK_KEY = "{IFTTT webhook key}"
WEBHOOK_EVENT = "alarm_activated"
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
# esp LED
WIFI_LED_PIN = Pin(16, Pin.OUT)

# # define signals
intruder_signal = Signal(INTRUDER_PIN, invert=True)
set_unset_signal = Signal(SET_UNSET_PIN, invert=True)
second_intruder_signal = Signal(SECOND_INTRUDER_PIN, invert=True)
wifi_LED = Signal(WIFI_LED_PIN, invert=True)
alarm_state = None


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


# actions
def check_intruder(intruder_signal_value, alarm_state):
    if intruder_signal_value is True and alarm_state is False:
        value1 = "alarm activated"
    elif intruder_signal_value is False and alarm_state is True:
        value1 = "alarm stopped"
    else:
        value1 = None
    return value1


def check_second_intruder(second_intruder_signal_value, second_intruder_state):
    if second_intruder_signal_value is True and second_intruder_state is False:
        value1 = "second intruder detected"
        return value1


def check_set(set_unset_signal_value, set_state):
    if set_unset_signal_value is True and set_state is False:
        value1 = "alarm set"
    elif set_unset_signal_value is False and set_state is True:
        value1 = "alarm unset"
    else:
        value1 = None
    return value1


def check_wifi_connected():
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


def send_webhook(url):
    full_url = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(url).encode()
    addr = socket.getaddrinfo(BASE_URL, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(full_url)
    # may not need to receive data, check if webhook works without and delete
    data = s.recv(1000)
    s.close()
    return True


def poll_alarm_signal(intruder_signal_value, alarm_state):
    sent_webhook = None
    value1 = check_intruder(intruder_signal_value, alarm_state)
    if value1 == "alarm activated":
        url = create_url(value1)
        sent_webhook = send_webhook(url)
        alarm_state = True
    elif value1 == "alarm stopped":
        alarm_state = False
    return alarm_state, sent_webhook


def poll_set_signal(set_unset_signal_value, set_state):
    value1 = check_set(set_unset_signal_value, set_state)
    sent_webhook = None
    if value1 == "alarm set":
        url = create_url(value1)
        sent_webhook = send_webhook(url)
        set_state = True
    elif value1 == "alarm unset":
        url = create_url(value1)
        set_state = False
    return set_state, sent_webhook


if __name__ == "__main__":
    if intruder_signal.value() != intruder_signal_value:
        intruder_signal_value = intruder_signal.value()
        alarm_state = poll_alarm_signal(intruder_signal_value, alarm_state)
    pass
