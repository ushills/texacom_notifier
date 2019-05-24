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


@pytest.fixture()
def intruder_signal_true():
    intruder_signal = Mock(spec=["value"])
    intruder_signal.value.return_value = True
    return intruder_signal


@pytest.fixture()
def intruder_signal_false():
    intruder_signal = Mock(spec=["value"])
    intruder_signal.value.return_value = False
    return intruder_signal


# test alarm signals
def test_alarm_signal_and_alarm_state_false(intruder_signal_true):
    alarm_state = False
    assert check_intruder(intruder_signal_true, alarm_state) == "alarm activated"


def test_alarm_signal_and_alarm_state_true(intruder_signal_false):
    alarm_state = True
    assert check_intruder(intruder_signal_false, alarm_state) is None


def test_no_alarm_signal_and_alarm_state_false(intruder_signal_false):
    alarm_state = False
    assert check_intruder(intruder_signal_false, alarm_state) is None


def test_no_alarm_signal_and_alarm_state_true(intruder_signal_false):
    alarm_state = True
    assert check_intruder(intruder_signal_false, alarm_state) is None


# test second intruder signals


@pytest.fixture()
def second_intruder_signal_true():
    second_signal = Mock(spec=["value"])
    second_signal.value.return_value = True
    return second_signal


@pytest.fixture()
def second_intruder_signal_false():
    second_signal = Mock(spec=["value"])
    second_signal.value.return_value = False
    return second_signal


def test_second_intruder_and_second_intruder_state_false(second_intruder_signal_true):
    second_intruder_state = False
    assert (
        check_second_intruder(second_intruder_signal_true, second_intruder_state)
        == "second intruder detected"
    )


def test_second_intruder_and_second_intruder_state_true(second_intruder_signal_true):
    second_intruder_state = True
    assert (
        check_second_intruder(second_intruder_signal_true, second_intruder_state)
        is None
    )


# test set/unset signals
def test_set_unset_signal_and_set_state_true():
    set_unset_signal = MagicMock()
    set_unset_signal.value.return_value = True
    set_state = False
    assert check_set(set_unset_signal, set_state) == "alarm set"


def test_set_unset_signal_and_set_state_false():
    set_unset_signal = MagicMock()
    set_unset_signal.value.return_value = False
    set_state = True
    assert check_set(set_unset_signal, set_state) == "alarm unset"


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

