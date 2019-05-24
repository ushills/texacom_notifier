import pytest
from unittest.mock import patch
from unittest.mock import MagicMock, Mock
import sys

# mock Signal and Pin from Micropython and not installed
mock_machine = MagicMock()
sys.modules["machine"] = mock_machine


# mock network from Micropython and not installed
mock_network = MagicMock()
sys.modules["network"] = mock_network

# mock usockect from Micropython and not installed
mock_usocket = MagicMock()
sys.modules["usocket"] = mock_usocket


from main import (
    create_url,
    check_intruder,
    check_second_intruder,
    check_set,
    send_webhook,
)


# patch global variables to isolate test case
@patch("main.WEBHOOK_KEY", "testWebhookKey")
@patch("main.WEBHOOK_EVENT", "testWebhookEvent")
def test_create_url():
    action = "alarm unset"
    assert (
        create_url(action)
        == "https://maker.ifttt.com/trigger/testWebhookEvent/with/key/testWebhookKey?value1=alarm unset"
    )


# test alarm signals
def test_alarm_signal_and_alarm_state_false():
    assert check_intruder(True, False) == "alarm activated"


def test_alarm_signal_and_alarm_state_true():
    assert check_intruder(True, True) is None


def test_no_alarm_signal_and_alarm_state_false():
    assert check_intruder(False, False) is None


def test_no_alarm_signal_and_alarm_state_true():
    assert check_intruder(False, True) is None


# test second intruder signals
def test_second_intruder_and_second_intruder_state_false():
    assert check_second_intruder(True, False) == "second intruder detected"


def test_second_intruder_and_second_intruder_state_true():
    assert check_second_intruder(True, True) is None


# test set signals
def test_set_signal_and_set_state_true():
    assert check_set(True, True) is None


def test_set_signal_and_set_state_false():
    assert check_set(True, False) == "alarm set"


# test unset signals
def test_unset_signal_and_set_state_true():
    assert check_set(False, True) == "alarm unset"


def test_unset_signal_and_set_state_false():
    assert check_set(False, False) is None


# check webook send functions
def fake_send_webhook(url):
    full_url = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(url).encode()
    return full_url


@patch("main.send_webhook", side_effect=fake_send_webhook)
def test_send_webhook(send_webhook):
    url = create_url("test action")
    full_url = send_webhook(url)
    assert type(full_url) == bytes
    assert (
        full_url
        == b"GET / HTTP/1.1\r\nHost: https://maker.ifttt.com/trigger/alarm_activated/with/key/{IFTTT webhook key}?value1=test action\r\n\r\n"
    )

