from unittest.mock import Mock, patch
from unittest.mock import MagicMock
from main import create_url, check_intruder, check_second_intruder, check_set


@patch("main.WEBHOOK_KEY", "testWebhookKey")
@patch("main.WEBHOOK_EVENT", "testWebhookEvent")
def test_create_url():
    action = "alarmunset"
    assert (
        create_url(action)
        == "https://maker.ifttt.com/trigger/testWebhookEvent/with/key/testWebhookKey?value1=alarmunset"
    )


# Test alarm signals
def test_alarm_signal_and_alarm_state_false():
    intruder_signal = MagicMock()
    intruder_signal.value.return_value = True
    alarm_state = False
    assert check_intruder(intruder_signal, alarm_state) == "alarm activated"


def test_alarm_signal_and_alarm_state_true():
    intruder_signal = MagicMock()
    intruder_signal.value.return_value = True
    alarm_state = True
    assert check_intruder(intruder_signal, alarm_state) is None


# test second intruder signals
def test_second_intruder_and_second_intruder_state_false():
    second_intruder_signal = MagicMock()
    second_intruder_signal.value.return_value = True
    second_intruder_state = False
    assert (
        check_second_intruder(second_intruder_signal, second_intruder_state)
        == "second intruder detected"
    )


def test_second_intruder_and_second_intruder_state_true():
    second_intruder_signal = MagicMock()
    second_intruder_signal.value.return_value = True
    second_intruder_state = True
    assert check_second_intruder(second_intruder_signal, second_intruder_state) is None


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

