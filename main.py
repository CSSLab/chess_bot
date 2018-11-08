import slack_handlers
import imitation_chess

import chess
import chess.svg

import cairosvg
import io

import time

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM

enginePath = 'lc0'
weightsSL = '/home/reidmcy/lczero-training/tf/networks/sl-64x6/sl-64x6-50000.pb.gz'

class EventsHandler(object):
    def __init__(self, client):
        self.client = client
        self.board = None
        self.channel = None
        self.movetime = 1000
        self.startTime = None

    def send(self, message, channel = None):
        if channel is None:
            channel = self.channel
        self.client.api_call(
            "chat.postMessage",
            channel=channel,
            text=message,
        )

    def postFile(self, content, channel = None, name = 'chess.png', comment = None):
        if channel is None:
            channel = self.channel
        self.client.api_call(
            "files.upload",
            channels=channel,
            file=content,
            filename=name,
            initial_comment=comment
            )

    def postBoard(self, board = None, **kargs):
        if board is None:
            board = self.board
        self.postFile(cairosvg.svg2png(board._repr_svg_()), **kargs)

    def makeEngineMove(self):
        m, p = self.Engine.getBoardProbs(self.board, movetime = self.movetime)
        self.board.push(m.bestmove)
        return m, p

    def handleEvent(self, message, channel):
        self.channel = channel
        if message == 'help':
            self.send("Help requested")
        elif message == 'start':
            if self.board is None:
                self.board = chess.Board()
                self.Engine = imitation_chess.EngineHandler(enginePath, weightsSL)
                self.send("Make your move")
                self.postBoard()
            else:
                self.send("Game already running, send 'stop' to end current game")
        elif message == 'stop':
            self.board = None
            self.Engine.terminate()
            self.send("Ending current game")

        elif message.startswith('movetime '):
            self.movetime = int(message.split()[1])

        elif self.board is not None:
            moves = [m.uci() for m in self.board.legal_moves]
            if message in moves:
                self.board.push_uci(message)
                self.postBoard()
                self.send("Making my move")
                m, p = self.makeEngineMove()
                self.postBoard()
                self.send("Probs:\n{}".format(p))
            if message == 'skip':
                self.send("Making my move")
                m, p = self.makeEngineMove()
                self.postBoard()
                self.send("Probs:\n{}".format(p))
            else:
                self.send("Invalid move, the valid moves are:\n{}".format(', '.join(moves)))
        else:
            self.send("Unkown command")

def checkIfmessage(event):
    if 'text' not in event:
        return False
    elif 'channel' not in event:
        return False
    elif 'user' not in event:
        return False
    elif event['type'] != 'message':
        return False
    elif event.get('name', '') == 'reidbot':
        return False
    elif event.get('username', '') == 'reid_bot':
        return False
    return True


def main():
    slack_client = slack_handlers.setup()
    Handler = EventsHandler(slack_client)
    while True:
        for event in slack_client.rtm_read():
            print(event)
            if checkIfmessage(event):
                Handler.handleEvent(event['text'], event['channel'])

        time.sleep(RTM_READ_DELAY)

if __name__ == "__main__":
    main()
