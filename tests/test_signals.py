import pytest
from unittest.mock import patch
from unittest.mock import MagicMock, Mock
import sys

# mock Signal and Pin from Micropython and not installed
mock_machine = MagicMock()
sys.modules["machine"] = mock_machine

from main import OutputManager
import main


def mock_OutputManager_trigger_command_return(command):
    return "trigger command actioned"


# @pytest.fixture(autouse=True)
# def mock_OutputManager_trigger_command(monkeypatch):
#     monkeypatch.setattr(
#         OutputManager, "trigger_command", mock_OutputManager_trigger_command_return
#     )


def test_output_is_active_starts_at_None():
    test_alarm = OutputManager()
    assert test_alarm.output_is_active is None


def test_triggering_alarm_changes_output_is_active_to_true():
    test_alarm = OutputManager()
    test_alarm.check_output(True)
    assert test_alarm.output_is_active is True


def test_triggering_alarm_triggers_command1(monkeypatch):
    test_alarm = OutputManager()
    monkeypatch.setattr(
        "main.OutputManager.trigger_command", mock_OutputManager_trigger_command_return
    )

    test_alarm.check_output(True)
    assert test_alarm.trigger_command() == "trigger command actioned"

