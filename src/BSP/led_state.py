

class LedState:
    """
    Holds information about the power status, color and the time of measurement of a single LED
    """

    def __init__(self, power, color, timestamp):
        self.power = power
        self.color = color
        self.timestamp = timestamp
