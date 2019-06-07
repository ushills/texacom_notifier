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


def mock_send_webhook(self, action):
    print("mocking send_webhook")
    url = (
        "http://maker.ifttt.com/trigger/{{webhook_event}}/with/key/{{webhook_key}}?value1="
        + action
    )
    _, _, host, path = url.split("/", 3)
    full_url = "GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n".format(path, host).encode()
    return full_url


@patch.object(Notifier, "send_webhook", mock_send_webhook)
class TestNotifier:
    @pytest.fixture(scope="class")
    def fake_signal(self):
        return Notifier()

    @pytest.fixture(scope="class")
    @patch.object(Notifier, "send_webhook", mock_send_webhook)
    def set_action1(self, fake_signal):
        fake_signal.set_action1("signal+activated")
        assert fake_signal.action1 == "signal+activated"

    @pytest.fixture(scope="class")
    @patch.object(Notifier, "send_webhook", mock_send_webhook)
    def set_action2(self, fake_signal):
        fake_signal.set_action2("signal+unactivated")
        assert fake_signal.action2 == "signal+unactivated"

    @pytest.fixture(scope="class")
    @patch.object(Notifier, "send_webhook", mock_send_webhook)
    def set_signal_true(self, fake_signal):
        fake_signal.check_signal(1)

    @pytest.fixture(scope="class")
    @patch.object(Notifier, "send_webhook", mock_send_webhook)
    def set_signal_false(self, fake_signal):
        fake_signal.check_signal(0)

    def test_signal_true_gives_signal_is_active(
        self, fake_signal, set_action1, set_signal_true
    ):
        assert fake_signal.signal_is_active is True

    def test_signal_false_gives_signal_is_not_active(
        self, fake_signal, set_action1, set_signal_false
    ):
        assert fake_signal.signal_is_active is False

    def test_create_url(self, fake_signal):
        assert (
            fake_signal.create_url("test+action")
            == "http://maker.ifttt.com/trigger/{{webhook_event}}/with/key/{{webhook_key}}?value1=test+action"
        )

    def test_send_webhook_value(self, fake_signal):
        assert (
            fake_signal.send_webhook(fake_signal.action1)
            == b"GET /trigger/{{webhook_event}}/with/key/{{webhook_key}}?value1=signal+activated HTTP/1.1\r\nHost: maker.ifttt.com\r\n\r\n"
        )

    def test_send_webhook_type(self, fake_signal):
        assert type(fake_signal.send_webhook("test+action")) == bytes

    def test_first_signal_sends_webhook(self, fake_signal):
        assert (
            fake_signal.check_signal(1)
            == b"GET /trigger/{{webhook_event}}/with/key/{{webhook_key}}?value1=signal+activated HTTP/1.1\r\nHost: maker.ifttt.com\r\n\r\n"
        )

    def test_second_signal_does_not_send_webhook(self, fake_signal, set_signal_true):
        # send second fake_signal signal
        assert fake_signal.check_signal(1) is None

    def test_sigal_deactivation_sends_ceased_response(
        self, fake_signal, set_signal_true
    ):
        assert fake_signal.check_signal(False) == "signal+activated ceased"

    def test_signal_deactivation_sends_action2_response_when_action2_exists(
        self, fake_signal, set_signal_true, set_action1, set_action2
    ):
        fake_signal.check_signal(True)
        assert (
            fake_signal.check_signal(False)
            == b"GET /trigger/{{webhook_event}}/with/key/{{webhook_key}}?value1=signal+unactivated HTTP/1.1\r\nHost: maker.ifttt.com\r\n\r\n"
        )
