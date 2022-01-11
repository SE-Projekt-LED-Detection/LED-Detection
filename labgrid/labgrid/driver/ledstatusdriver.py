import attr

from .common import Driver
from ..factory import target_factory

from ..protocol import PowerProtocol


@target_factory.reg_driver
@attr.s(eq=False)
class LEDStatusDriver(Driver, PowerProtocol):
    bindings = {
            "led": {"LEDStatus"}
    }

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        import paho.mqtt.client as mqtt
        self._client = mqtt.Client()

    def on(self):
        pass

    def off(self):
        pass

    def cycle(self):
        pass

