from unittest.mock import patch
from main import create_url


@patch("main.WEBHOOK_KEY", "testWebhookKey")
@patch("main.WEBHOOK_EVENT", "testWebhookEvent")
def test_create_url():
    action = "alarmunset"
    assert create_url(action) == 'https://maker.ifttt.com/trigger/testWebhookEvent/with/key/testWebhookKey?value1=alarmunset'
