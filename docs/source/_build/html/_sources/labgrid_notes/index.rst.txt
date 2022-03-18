.. _labgrid_notes:

Labgrid
=======

Sinse the `labgrid documentation <https://labgrid.readthedocs.io/en/latest/index.html>`_,
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