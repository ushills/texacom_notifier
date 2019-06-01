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
        test_signal.action1 = "signal activated"

    @pytest.fixture(scope="class")
    def set_action2(self, test_signal):
        test_signal.action2 = "signal unactivated"

    @pytest.fixture(scope="class")
    def set_signal_true(self, test_signal):
        test_signal.check_signal(True)

    @pytest.fixture(scope="class")
    def set_signal_false(self, test_signal):
        test_signal.check_signal(False)

    def mock_action1_return(self):
        return "action1 sent"

    # @pytest.fixture(autouse=True)
    # def mock_send_action1(monkeypatch):
    #     monkeypatch.setattr("main.Notifier.send_action1", "action1 sent")

    def test_signal_true_gives_signal_is_active(
        self, test_signal, set_action1, set_signal_true
    ):
        assert test_signal.signal_is_active is True

    def test_signal_false_gives_signal_is_not_active(
        self, test_signal, set_action1, set_signal_false
    ):
        assert test_signal.signal_is_active is False

    def test_signal_true_triggers_send_action1(self, test_signal, set_action1):
        assert test_signal.check_signal(True) == "action1 sent"

    # def test_signal_true_trigger_command_return(
    #     self, test_signal, set_action1, set_signal_true
    # ):
    #     assert test_signal.send_action1 == "action1 sent"
