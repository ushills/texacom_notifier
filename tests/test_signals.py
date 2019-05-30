import pytest
from unittest.mock import patch
from unittest.mock import MagicMock, Mock
import sys

# mock Signal and Pin from Micropython and not installed
mock_machine = MagicMock()
sys.modules["machine"] = mock_machine

from main import OutputManager

# create an instance of OutputManager
@pytest.fixture(scope="module")
def alarm_output():
    return OutputManager()


# mock the commands


class TestAlarmDoesNotTriggerOutput:
    # do not trigger the output
    @pytest.fixture(scope="class", autouse="True")
    def alarm_output_is_not_active(self, alarm_output):
        alarm_output.check_output(False)

    def test_the_output_is_not_active(self, alarm_output):
        assert not alarm_output.output_is_active


class TestTriggerOutput:
    # trigger the output
    @pytest.fixture(scope="class", autouse="True")
    def alarm_output_is_active(self, alarm_output):
        alarm_output.check_output(True)

    def test_the_output_is_active(self, alarm_output):
        assert alarm_output.output_is_active


def test_alarm_triggers_trigger_command():
    test_alarm = OutputManager()
    alarm_output.check_output(True)
    assert test_alarm.output_is_active

