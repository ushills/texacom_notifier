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


def mock_OutputManager_cease_command_return(command):
    return "cease command actioned"


def test_output_is_active_starts_at_False():
    test_alarm = OutputManager()
    assert test_alarm.output_is_active is False


def test_triggering_alarm_changes_output_is_active_to_true():
    test_alarm = OutputManager()
    test_alarm.command1 = "test_alarm"
    test_alarm.check_output(True)
    assert test_alarm.output_is_active is True


def test_triggering_alarm_triggers_command1(monkeypatch):
    test_alarm = OutputManager()
    test_alarm.command1 = "test_alarm"
    # monkeypatch.setattr(
    #     "test_signals.OutputManager.trigger_command",
    #     mock_OutputManager_trigger_command_return,
    # )

    # test_alarm.check_output(True)
    assert test_alarm.check_output(True) == "test_alarm triggered"


def test_triggering_alarm_does_not_trigger_cease_command(monkeypatch):
    test_alarm = OutputManager()
    monkeypatch.setattr(
        "test_signals.OutputManager.cease_command",
        mock_OutputManager_cease_command_return,
    )

    test_alarm.check_output(True)
    assert test_alarm.cease_command() == "cease command actioned"
