import typing


class Config:
    """
    Configuration for the MQTT subscriber.
    """

    def __init__(self, broker_address: str, broker_port: int, topics=""):
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.broker_keepalive = 60
        self.topics = topics

    def __str__(self) -> str:
        return f"Config(broker_address={self.broker_address}, broker_port={self.broker_port}, topics={self.topics})"