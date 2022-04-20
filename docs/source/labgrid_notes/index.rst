.. _labgrid_notes:

Add Labgrid LED command
=======================

Setup:
------

For the labgrid client we follow the official documentation but instead of the official repository for labgrid we use our own
    
    .. code-block:: bash

        $ virtualenv -p python3 labgrid-venv
        $ source labgrid-venv/bin/activate
        labgrid-venv $ git clone https://github.com/12rcu/labgrid
        labgrid-venv $ cd labgrid && pip install -r requirements.txt
        labgrid-venv $ python3 setup.py install

Follow the `official setup <https://labgrid.readthedocs.io/en/latest/getting_started.html#coordinator>`_ for the coordinator and the exporter.

Usage
-----

MQTT Driver:
    First add a ``MQTTResource`` for the Exporter. A sample for this config would be:
    
    .. code-block:: yaml

        <resource-group>:
            MQTTResource:
                host: 127.0.0.1

    Add this group to a place and acquire it with the labgrid-client.
    Now we can access the ``mqtt`` subcommand within the client:

    .. code-block:: bash

        labgrid-venv $ labgrid-client -p <place> mqtt -s $Sys/# -t -1

    while the ``-s`` or ``--subscribe`` flag takes a string and tries to subscribe to ist. (the ``#`` means that all subtopics should be subscribed)
    The ``-t`` or ``--time`` flag takes a float in seconds. After the time the client terminates and closes the connection to the broker,
    -1 for infinite.

LED Driver:
    First add a ``LEDBoardTopic`` resource to configuration of the Exporter. A sample for this config would be:

    .. code-block:: yaml

        <resource-group>:
            LEDBoardTopic:
                host: 127.0.0.1
                board_topic: changes/zcu102

    While ``zcu201`` the board identifier from the Bord-detection config  is.
    Add this group to a place and acquire it with the labgrid-client.
    Now we can access the ``led`` subcommand within the client:

    .. code-block:: bash

        labgrid-venv $ labgrid-client -p <place> led <topic1/subtopic> <topic2> <...>


    While ``#`` is again a white card for all subtopic, some examples of possible topics ::

        topic/subtopic
        topic/#
        #
    
    Note: The topic ``all`` is equivalent to the topic ``#`` and is used to make the command more readable:

    .. code-block:: bash

        labgrid-venv $ labgrid-client -p <place> led all

MQTT Driver/Resource/Client Documentation
=========================================

All the relevant code blocks as the labgrid project itself is quite complex:

Resources
---------

Found in ``labgrid/resource``

MQTTManager:
    
    .. code-block:: python

        @attr.s(eq=False)
        class MQTTManager(ResourceManager):
            # set default components
            _available = attr.ib(default=attr.Factory(set), validator=attr.validators.instance_of(set))
            _avail_lock = attr.ib(default=threading.Lock())
            _clients = attr.ib(default=attr.Factory(dict), validator=attr.validators.instance_of(dict))
            _topics = attr.ib(default=attr.Factory(list), validator=attr.validators.instance_of(list))
            _topic_lock = attr.ib(default=threading.Lock())
            _last = attr.ib(default=0.0, validator=attr.validators.instance_of(float))

            def __attrs_post_init__(self):
                super().__attrs_post_init__()
                self.log = logging.getLogger('MQTTManager')

            # create the connection to the broker when a resource was found/added
            def _create_mqtt_connection(self, host):
                import paho.mqtt.client as mqtt
                client = mqtt.Client()
                client.connect(host)
                client.on_connect = self._on_connect
                client.on_message = self._on_message
                client.loop_start()
                return client

            def on_resource_added(self, resource):
                host = resource.host
                if host not in self._clients:
                    self._clients[host] = self._create_mqtt_connection(host)
                self._clients[host].subscribe(resource.avail_topic)
        
            def _on_message(self, client, userdata, msg):
                # print(f"<resource> mqtt message in topic {msg.topic} received with payload: {msg.payload.decode('utf-8')}")
                payload = msg.payload.decode('utf-8')
                topic = msg.topic
                
                with self._avail_lock:
                        self._available.add(topic) 
                        
            def _on_connect(self, client, userdata, flags, rc):
                if rc == 0:
                    print("<resource> Connected to MQTT Broker!")
                else:
                    print("<resource> Failed to connect, return code %d\n", rc)
        
        
            def poll(self):
                if monotonic()-self._last < 2:
                    return  # ratelimit requests
                self._last = monotonic()
                with self._avail_lock:
                    for resource in self.resources:
                        resource.avail = resource.avail_topic in self._available

The MQTTResource is also added from a newer version and defines within the exporter the host topic and the avail topic. 

    .. code-block:: python

        @target_factory.reg_resource
        @attr.s(eq=False)
        class MQTTResource(ManagedResource):    # depends on ManagedResource
            manager_cls = MQTTManager
        
            host = attr.ib(validator=attr.validators.instance_of(str))
            avail_topic = attr.ib(validator=attr.validators.instance_of(str))
        
            def __attrs_post_init__(self):
                self.timeout = 120.0
                super().__attrs_post_init__()

For the mqtt driver is this resource enough, for the led driver we also want to define a topic where the board publishes it's events:

    .. code-block:: python

        @target_factory.reg_resource
        @attr.s(eq=False)
        class LEDBoardTopic(MQTTResource):    # depends on MQTTResource
            board_topic = attr.ib(default=None, validator=attr.validators.instance_of(str))

Driver
-----

Found in ``labgrid/driver``

MQTT Driver

The client will set the subscribed_topic variable to the topic that was subscribed. After the driver was acivated the driver will then connect itself to the MQTT Broker and will proceed to subscribe to the topic that was set in the variable. 

    .. code-block:: python

        @target_factory.reg_driver
        @attr.s(eq=False)
        class MQTTDriver(Driver):
            bindings = {
                    "mqtt": {"MQTTResource"}
            }
            subscribed_topic = ""
            
            def __attrs_post_init__(self):
                super().__attrs_post_init__()
                import paho.mqtt.client as mqtt
                self._client = mqtt.Client()
                
            def on_activate(self):
                print(f"<driver> mqtt driver active")
                self._client.on_message = self._on_message
                self._client.on_connect = self._on_connect
                self._client.connect(self.mqtt.host)
                self._client.loop_start()
                
            def _on_connect(self, client, userdata, flags, rc):
                if(self.subscribed_topic != ""):
                    self._client.subscribe(self.subscribed_topic)
                print(f"<driver> mqtt client connected")
        
            def _on_message(self, client, userdata, msg):
                print(f"<driver> topic: {msg.topic} payload: {msg.payload}")
                self.payload = msg.payload

LED Driver

The led driver gets a list from the client of topics to which it should subscribe to. If the topic is empty the driver subscribes to all topics the board provides.

        .. code-block:: python

            @target_factory.reg_driver
            @attr.s(eq=False)
            class LEDBoardTopicDriver(Driver):
                bindings = {
                        "board": {"LEDBoardTopic"}
                }
                subscribed_topics = []
                
                def __attrs_post_init__(self):
                    super().__attrs_post_init__()
                    import paho.mqtt.client as mqtt
                    self._client = mqtt.Client()
                    
                def on_activate(self):
                    self._client.on_message = self._on_message
                    self._client.on_connect = self._on_connect
                    self._client.connect(self.board.host)
                    self._client.loop_start()
                    
                def _on_connect(self, client, userdata, flags, rc):
                    print(f"<mqtt-driver> mqtt client connected")
                    for i in self.subscribed_topics:
                        # i.removePrefix("/") # not supported in the current python version
                        if i != "all":
                            self._client.subscribe(self.board.board_topic + "/" + i)
                            print("<mqtt-driver> subscribe to " + self.board.board_topic + "/" + i)
                        else:
                            self._client.subscribe(self.board.board_topic)
                            print("<mqtt-driver> subscribe to " + self.board.board_topic)
            
                def _on_message(self, client, userdata, msg):
                    print(f"<mqtt-driver> topic: {msg.topic} payload: {msg.payload}")
                    self.payload = msg.payload

Client
------
found in ``labgrid/remote/client.py``

MQTT

Commandline Args

    .. code-block:: python

        subparser = subparsers.add_parser('mqtt',
                                         aliases=('MQTT'),
                                         help="get a topic from a mqtt brker")
        subparser.add_argument('-s', '--subscribe', default="",
                               help='wait time in seconds for msgs to arrive, -1 for infinit wait')
        subparser.add_argument('-t', '--time', type=float, default=float(-1),
                               help='wait time in seconds for msgs to arrive, -1 for infinit wait')
        subparser.set_defaults(func=ClientSession.mqtt)

Calling the driver:

    .. code-block:: python

        async def mqtt(self):
            place = self.get_acquired_place()
            target = self._get_target(place)
            topic = self.args.subscribe
            time = self.args.time
            
            from ..driver.mqtt import MQTTDriver
            try:
                drv = target.get_driver(MQTTDriver)
            except NoDriverFoundError:
                drv = MQTTDriver(target, name=None)
            
            drv.subscribed_topic = topic
            target.activate(drv)
        
            if(time < 0):
                while True:
                    await asyncio.sleep(1.0)
            else:
                from ..util import Timeout
                timeout = Timeout(time)
                while True:
                    await asyncio.sleep(1.0)
                    if timeout.expired:
                        break    

LED

Commandline Args

    .. code-block:: python

        subparser = subparsers.add_parser('led',
                                         aliases=('leddet'),
                                         help="get the current LED statues of a place's boards")
        subparser.add_argument('-t', '--time', type=float, default=float(-1),
                              help='wait time in seconds for msgs to arrive, -1 for infinit wait')
        subparser.add_argument('topics', help="optional topic to subscribe, blank for all", nargs='+')
        subparser.set_defaults(func=ClientSession.led)


Calling/initialising the driver:

    .. code-block:: python

        async def led(self): 
            place = self.get_acquired_place()
            topics = self.args.topics
            target = self._get_target(place)
            time = self.args.time
            
            from ..driver.mqtt import LEDBoardTopicDriver
            try:
                drv = target.get_driver(LEDBoardTopicDriver)
            except NoDriverFoundError:
                drv = LEDBoardTopicDriver(target, name=None)
            
            drv.subscribed_topics = topics
            target.activate(drv)
            
            if time < 0:
                while True:
                    await asyncio.sleep(1.0)
            else:
                from ..util import Timeout
                timeout = Timeout(time)
                while True:
                    await asyncio.sleep(1.0)
                    if timeout.expired:
                        break


Labgrid developer notes:
========================

Since the `labgrid documentation <https://labgrid.readthedocs.io/en/latest/index.html>`_,
was a bit confusing for us we want to add some notes and experience on
how to write a proper Driver.

Steps for creating a Resource:
-------------------------------

   
At first you have to import the Driver module as well as the `attr <https://www.attrs.org/en/stable/>`_ module

    .. code-block:: python
    

    
        import attr

Than you have to deside what kind of resource you want to create.

There are:

* Resource: Represents a resource which is used by drivers. It only stores information and does not implement any actual functionality.
* NetworkResource: Represents a remote Resource available on another computer.
* ManagedResource: Represents a resource which can appear and disappear at runtime. Every ManagedResource has a corresponding ResourceManager which handles these events.

In Case of our LED Driver we want to create a ManagedResource sinse we want to connect and disconnect with a broker
and want to send informations.

Because of that we also need to create a ResourceManager.

    .. code-block:: python
    

        import attr
        from labgrid.resource import ResourceManager, Resource


Labgrid uses factories for the automatic instanciation.
To register our Resource we add that:

    .. code-block:: python
    

        import attr
        from labgrid.factory import target_factory
        from labgrid.resource import ResourceManager, Resource

        @target_factory.reg_resource
        @attr.s(eq=False)
        class ExampleResourceManager(ResourceManager):
            examplevar1 = attr.ib()
            examplevar2 = attr.ib()