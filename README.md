# ESP8266/NodeMCU notifier for Texacom Communicator Interface

Code for Texecom Veritas Alarm communicator inteface
using esp8266 - Nodemcu Development Kit to send alarm
communications to IFTTT to trigger external responses

---

Output from communicator ports is 12V+ and a voltage
divider is required to reduce to 3.3V.
use 10k(R1) and 3.3k(R2) to step down 12-13v > 3.3V

**Communicator Interface Channels**

- Channel 3 = Intruder
- Channel 4 = Set/Unset
- Channel 8 = 2nd Intruder (Sequentally confirmed alarm)
- R/R can be used for remote reset but not currently implemented

Pins are high by default and therefore a value of 0 indicates
an alarm state

---

The Notifier class checks the inputs from a signal and depending on the
input triggers certain external actions, in this case triggering a webhook
using IFTTT.

The class has the following methods for direct use:

    check_signal(signal_input) - checks the signal and triggers the webhook
        if the signal state has changed.
    set_action1(str) - sets the action(value1) to be sent with the webhook.
    set_action2(str) - sets the action(value2) to be sent with the webhook.

The following methods are exposed but are not intended for direct use but
are available for testing purposes:

    create_url(str) - creates a url in the format required by IFTTT to
        trigger the webhook.
    send_webhook(str) - creates the full url required for Micropython usocket,
        from create_url, creates a socket connection and sends the webhook.


