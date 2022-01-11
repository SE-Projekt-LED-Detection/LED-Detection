import attr

from ..factory import target_factory
from mqtt import MQTTResource


@target_factory.reg_resource
@attr.s(eq=False)
class LEDStatus(MQTTResource):
    sample1_topic = attr.ib(default=None, validator=attr.validators.instance_of(str))
    sample2_topic = attr.ib(default=None, validator=attr.validators.instance_of(str))
