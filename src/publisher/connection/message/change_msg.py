import logging


class BoardChanges:
    def __init__(self, board, id, value, color, frequency, time):
        self.id = id
        self.time = time
        self.board = board
        self.value = value
        self.color = color
        self.frequency = frequency

    def log(self):
        logging.info("Time: %s Led %s on board %s new state: %s with color %s and frequency %s", str(self.time), str(self.id), self.board, self.value, self.color, str(self.frequency))


