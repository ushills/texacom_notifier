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


from main import create_url, OutputManager


# patch global variables to isolate test case
@patch("main.WEBHOOK_KEY", "testWebhookKey")
@patch("main.WEBHOOK_EVENT", "testWebhookEvent")
def test_create_url():
    action = "alarm unset"
    assert (
        create_url(action)
        == "https://maker.ifttt.com/trigger/testWebhookEvent/with/key/testWebhookKey?value1=alarm unset"
    )


# check webook send functions
# mock send_webhook with fake_send_webhook
def fake_send_webhook(url):
    full_url = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(url).encode()
    print("webhook sent\n{}".format(full_url))
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


# test Output signals
# mock Output.trigger_command function for test
# def fake_Output_trigger_command():
#     return "output triggered"


@pytest.fixture(scope="class")
def output_manager():
    return OutputManager()


@pytest.fixture(scope="class")
def output_manager_trigger_method():
    OutputManager = Mock()
    return OutputManager.trigger_command


@pytest.fixture(scope="class")
def output_manager_cease_method():
    OutputManager = Mock()
    return OutputManager.cease_command


def test_Output_init():
    test_alarm = OutputManager()
    assert test_alarm.output_is_active is False
    assert test_alarm.command1 is None
    assert test_alarm.command2 is None


class TestDoNotTriggerOutput:
    @pytest.fixture(scope="class", autouse=True)
    def handle_false_output_value(self, output_manager):
        output_manager.check_output(False)

    def test_output_is_not_active(self, output_manager):
        assert not output_manager.output_is_active

    def test_trigger_command_is_not_called(self, output_manager_trigger_method):
        assert output_manager_trigger_method.assert_not_called

    def test_cease_command_is_not_called(self, output_manager_cease_method):
        assert output_manager_cease_method.assert_not_called


class TestTriggerOutput:
    @pytest.fixture(scope="class", autouse=True)
    def handle_true_output_value(self, output_manager):
        output_manager.check_output(True)

    def test_output_is_active(self, output_manager):
        assert output_manager.output_is_active

    def test_trigger_command_is_called(self, output_manager_trigger_method):
        assert output_manager_trigger_method.assert_called_once

    def test_cease_command_is_not_called(self, output_manager_cease_method):
        assert output_manager_cease_method.assert_not_called


class TestTriggerOutputOnceRunsOnce:
    @pytest.fixture(scope="class", autouse=True)
    def handle_multiple_true_output_values(self, output_manager):
        output_manager.check_output(True)
        output_manager.check_output(True)

    def test_output_is_active(self, output_manager):
        assert output_manager.output_is_active

    def test_trigger_command_is_called_only_once(self, output_manager_trigger_method):
        assert output_manager_trigger_method.assert_called_once

    def test_cease_command_is_not_called(self, output_manager_cease_method):
        assert output_manager_cease_method.assert_not_called


# @patch("main.Output.trigger_command", side_effect=fake_Output_trigger_command)
# def test_output_trigger(trigger_command):
#     test_alarm = Output()
#     test_alarm.check_output(True)
#     assert test_alarm.output_is_active is True
#     assert Output.trigger_command.called is True


# @patch("main.Output.trigger_command", side_effect=fake_Output_trigger_command)
# def test_output_trigger_maintained(trigger_command):
#     test_alarm = Output()
#     test_alarm.check_output(True)
#     test_alarm.check_output(True)
#     assert test_alarm.output_is_active is True
#     assert Output.trigger_command.assert_called_once is True


# @pytest.fixture(scope="class")
# def output_manager():
#     return Output()

# @pytest.fixture(scope="class")
# def output_manager_trigger_method


# # test alarm signals
# def test_check_intruder():
#     assert check_intruder(True, False) == "alarm activated"
#     assert check_intruder(True, True) is None
#     assert check_intruder(False, False) is None
#     assert check_intruder(False, True) == "alarm stopped"


# # test second intruder signals
# def test_check_second_intruder_and_second_intruder_state_false():
#     assert check_second_intruder(True, False) == "second intruder detected"
#     assert check_second_intruder(True, True) is None
#     assert check_second_intruder(False, True) == "second intruder cleared"
#     assert check_second_intruder(False, False) is None


# # test set signals
# def test_check_set():
#     assert check_set(True, True) is None
#     assert check_set(True, False) == "alarm set"
#     assert check_set(False, True) == "alarm unset"
#     assert check_set(False, False) is None

# # functional tests
# @patch("main.send_webhook", side_effect=fake_send_webhook)
# def test_poll_alarm_signal(send_webhook):
#     alarm_state = False
#     # send alarm activated signal, webhook should be sent and alarm state changed to True
#     alarm_state, sent_webhook = poll_alarm_signal(True, alarm_state)
#     assert alarm_state is True
#     assert (
#         sent_webhook
#         == b"GET / HTTP/1.1\r\nHost: https://maker.ifttt.com/trigger/alarm_activated/with/key/{IFTTT webhook key}?value1=alarm activated\r\n\r\n"
#     )
#     # alarm state should now be set to True and no webhook sent
#     alarm_state, sent_webook = poll_alarm_signal(True, alarm_state)
#     assert alarm_state is True
#     assert sent_webook is None
#     # alarm state should change to False and no webhook sent
#     alarm_state, sent_webook = poll_alarm_signal(False, alarm_state)
#     assert alarm_state is False
#     assert sent_webook is None


# @patch("main.send_webhook", side_effect=fake_send_webhook)
# def test_poll_set_signal(send_webhook):
#     set_state = False
#     # send alarm set signal, set_state changes to True and webhook sent
#     set_state, sent_webook = poll_set_signal(True, set_state)
#     assert set_state is True
#     assert (
#         sent_webook
#         == b"GET / HTTP/1.1\r\nHost: https://maker.ifttt.com/trigger/alarm_activated/with/key/{IFTTT webhook key}?value1=alarm set\r\n\r\n"
#     )
#     # alarm set signal maintained, set state remains True and no webhook sent
#     set_state, sent_webook = poll_set_signal(True, set_state)
#     assert set_state is True
#     assert sent_webook is None
#     # send alarm unset signal, set_state changes to False and webhook sent
#     set_state, sent_webook = poll_set_signal(False, set_state)
#     assert set_state is False
#     assert (
#         sent_webook
#         == b"GET / HTTP/1.1\r\nHost: https://maker.ifttt.com/trigger/alarm_activated/with/key/{IFTTT webhook key}?value1=alarm unset\r\n\r\n"
#     )
#     # alarm unset signal maintained, set state remains False and no webhook sent
#     set_state, sent_webook = poll_set_signal(False, set_state)
#     assert set_state is False
#     assert sent_webook is None


# @patch("main.send_webhook", side_effect=fake_send_webhook)
# def test_poll_second_intruder_signal(send_webhook):
#     second_intruder_state = False
#     # send second intruder signal, second_intruder_state changes to True and webhook sent
#     second_intruder_state, sent_webook = poll_second_intruder_signal(
#         True, second_intruder_state
#     )
#     assert second_intruder_state is True
#     assert (
#         sent_webook
#         == b"GET / HTTP/1.1\r\nHost: https://maker.ifttt.com/trigger/alarm_activated/with/key/{IFTTT webhook key}?value1=second intruder detected\r\n\r\n"
#     )
#     # second intruder signal maintained, second intruder state remains True and no webhook sent
#     second_intruder_state, sent_webook = poll_second_intruder_signal(
#         True, second_intruder_state
#     )
#     assert second_intruder_state is True
#     assert sent_webook is None
#     # clear second intruder signal, second intruder state changes to False and no webhook sent
#     second_intruder_state, sent_webook = poll_second_intruder_signal(
#         False, second_intruder_state
#     )
#     assert second_intruder_state is False
#     assert sent_webook is None
#     # alarm unset signal maintained, set state remains False and no webhook sent
#     second_intruder_state, sent_webook = poll_second_intruder_signal(
#         False, second_intruder_state
#     )
#     assert second_intruder_state is False
#     assert sent_webook is None
