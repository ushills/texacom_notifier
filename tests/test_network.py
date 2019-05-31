import pytest
from unittest.mock import MagicMock
import sys

# # mock Signal and Pin from Micropython and not installed
mock_machine = MagicMock()
sys.modules["machine"] = mock_machine


# mock network from Micropython and not installed
mock_network = MagicMock()
sys.modules["network"] = mock_network

# mock usockect from Micropython and not installed
mock_usocket = MagicMock()
sys.modules["usocket"] = mock_usocket


import main


@pytest.fixture(autouse=True)
def redefine_webhook_variables():
    main.WEBHOOK_KEY = "testWebhookKey"
    main.WEBHOOK_EVENT = "testWebhookEvent"


def test_create_url(redefine_webhook_variables):
    action = "testAction"
    assert (
        main.create_url(action)
        == "https://maker.ifttt.com/trigger/testWebhookEvent/with/key/testWebhookKey?value1=testAction"
    )


def mock_send_webhook_return(url):
    full_url = "GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(url).encode()
    return full_url


@pytest.fixture(autouse=True)
def mock_send_webhook(monkeypatch):
    monkeypatch.setattr(main, "send_webhook", mock_send_webhook_return)


def test_send_webhook_is_bytes(mock_send_webhook):
    url = "testUrl"
    assert type(main.send_webhook(url)) == bytes


def test_send_webhook_url(mock_send_webhook):
    url = "testUrl"
    assert main.send_webhook(url) == b"GET / HTTP/1.1\r\nHost: testUrl\r\n\r\n"
