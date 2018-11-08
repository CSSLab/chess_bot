import slack_handlers

import time

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM

class EventsHandler(object):
    def __init__(self, client):
        self.client = client

    def send(self, message, channel):
        self.client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message,
        )

    def handleEvent(self, message, channel):
        if message == 'help':
            self.send("Help requested", channel)
        else:
            self.send("Unkown command", channel)






def main():
    slack_client = slack_handlers.setup()
    Handler = EventsHandler(slack_client)
    while True:
        for event in slack_client.rtm_read():
            print(event)
            if event['type'] == 'message' and 'bot_id' not in event:
                Handler.handleEvent(event['text'], event['channel'])
        time.sleep(RTM_READ_DELAY)

if __name__ == "__main__":
    main()
