import logging
import pkgutil

from maltego_trx.transform import DiscoverableTransform

log = logging.getLogger("maltego.discovery")
module_name = "transforms"

transform_functions = []
transform_classes = []


def register_transform_function(transform_function):
    # Register a transform function with the server.
    global transform_functions
    if transform_function not in transform_functions:
        transform_functions.append(transform_function)
    else:
        log.warning("Transform function already registered.")


def register_transform_classes(module):
    # Register transform classes from a given python module
    global transform_classes

    prefix = module.__name__ + "."  # transform.
    for importer, modname, ispkg in pkgutil.iter_modules(module.__path__, prefix):
        if not ispkg:
            module = __import__(modname, fromlist="dummy")
            name = module.__name__.replace(prefix, '')  # strip transform. prefix from module name

            if hasattr(module, name):  # Does the .py file have a class of the same name.
                transform_cls = getattr(module, name)
                if issubclass(transform_cls, DiscoverableTransform):  # Does the class subclass MaltegoTransform
                    transform_classes.append(transform_cls)
            else:
                log.info('Ignoring File: "%s" does not contain a class of the same name' % name)


def print_registered():
    print("Transform Functions:")
    for func in transform_functions:
        print(func.__name__)
    print("")
    print("Transform Classes:")
    for cls in transform_classes:
        print(cls.__name__)