import slack_handlers

import chess
import chess.svg

import cairosvg
import io

import time

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM

class EventsHandler(object):
    def __init__(self, client):
        self.client = client
        self.board = None

    def send(self, message, channel):
        self.client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message,
        )

    def postFile(self, content, channel, name = 'chess.png', comment = None):
        self.client.api_call(
            "files.upload",
            channels=channel,
            file=content,
            filename=name,
            initial_comment=comment
            )

    def postBoard(self, board, channel, **kargs):
        self.postFile(cairosvg.svg2png(board._repr_svg_()), channel, **kargs)

    def handleEvent(self, message, channel):
        if message == 'help':
            self.send("Help requested", channel)
        elif message == 'start':
            if self.board is None:
                self.board = chess.Board()
                self.send("Black or White?", channel)

                self.postBoard(self.board)

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
