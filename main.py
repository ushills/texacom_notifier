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
def check_intruder(intruder_signal, alarm_state):
    if intruder_signal.value() is True and alarm_state is False:
        signal = "alarm activated"
        # send_webhook(signal)
        return signal


def check_second_intruder(second_intruder_signal, second_intruder_state):
    if second_intruder_signal.value() is True and second_intruder_state is False:
        signal = "second intruder detected"
        return signal


def check_set(set_unset_signal, set_state):
    if set_unset_signal.value() is True and set_state is False:
        signal = "alarm set"
        send_webhook(signal)
        return signal
    elif set_unset_signal.value() is False and set_state is True:
        signal = "alarm unset"
        return signal


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


def send_webhook(webhook):
    pass


if __name__ == "__main__":
    pass
