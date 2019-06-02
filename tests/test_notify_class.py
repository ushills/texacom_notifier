import pytest
from unittest.mock import patch
from unittest.mock import MagicMock, Mock
import sys

# mock Signal and Pin from Micropython and not installed
mock_machine = MagicMock()
sys.modules["machine"] = mock_machine

mock_network = MagicMock()
sys.modules["network"] = mock_network

mock_usocket = MagicMock()
sys.modules["usocket"] = mock_usocket

from main import Notifier
import main


"""create an instance of Notifier 
   called test_signal as a base for testing
"""


class TestNotifier:
    @pytest.fixture(scope="class")
    def test_signal(self):
        return Notifier()

    @pytest.fixture(scope="class")
    def set_action1(self, test_signal):
        test_signal.set_action1("signal activated")
        assert test_signal.action1 == "signal activated"

    @pytest.fixture(scope="class")
    def set_action2(self, test_signal):
        test_signal.set_action2("signal unactivated")
        assert test_signal.action2 == "signal unactivated"

    @pytest.fixture(scope="class")
    def set_signal_true(self, test_signal):
        test_signal.check_signal(True)

    @pytest.fixture(scope="class")
    def set_signal_false(self, test_signal):
        test_signal.check_signal(False)

    def test_signal_true_gives_signal_is_active(
        self, test_signal, set_action1, set_signal_true
    ):
        assert test_signal.signal_is_active is True

    def test_signal_false_gives_signal_is_not_active(
        self, test_signal, set_action1, set_signal_false
    ):
        assert test_signal.signal_is_active is False

    def test_create_url(self, test_signal):
        assert (
            test_signal.create_url("test action")
            == "https://maker.ifttt.com/trigger/{{webhook_event}}/with/key/{{webhook_key}}?value1=test action"
        )

    def test_send_webhook_value(self, test_signal):
        assert (
            test_signal.send_webhook("test action")
            == b"GET / HTTP/1.1\r\nHost: https://maker.ifttt.com/trigger/{{webhook_event}}/with/key/{{webhook_key}}?value1=test action\r\n\r\n"
        )

    def test_send_webhook_type(self, test_signal):
        assert type(test_signal.send_webhook("test action")) == bytes

    def test_first_signal_sends_webhook(self, test_signal):
        assert (
            test_signal.check_signal(True)
            == b"GET / HTTP/1.1\r\nHost: https://maker.ifttt.com/trigger/{{webhook_event}}/with/key/{{webhook_key}}?value1=signal activated\r\n\r\n"
        )

    def test_second_signal_does_not_send_webhook(self, test_signal, set_signal_true):
        # send second test_signal signal
        assert test_signal.check_signal(True) is None

    def test_sigal_deactivation_sends_ceased_response(self, test_signal, set_signal_true):
        assert test_signal.check_signal(False) == "signal activated ceased"

    def test_signal_deactivation_sends_action2_response_when_action2_exists(
        self, test_signal, set_signal_true, set_action1, set_action2
    ):
        test_signal.check_signal(True)
        assert (
            test_signal.check_signal(False)
            == b"GET / HTTP/1.1\r\nHost: https://maker.ifttt.com/trigger/{{webhook_event}}/with/key/{{webhook_key}}?value1=signal unactivated\r\n\r\n"
        )

