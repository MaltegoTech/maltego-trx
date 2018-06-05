import logging
import pkgutil

import transforms
from libs.transform import DiscoverableTransform

log = logging.getLogger("maltego.discovery")
module_name = "transforms"


def discover_transforms(module):  # Get transforms from a given module
    transform_classes = []

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

    return transform_classes


def get_transforms():
    """
    Discover transforms from the project's "transforms" folder.
    """
    mapping = {}
    all_transforms = discover_transforms(transforms)
    for transform_cls in all_transforms:
        mapping[transform_cls.__name__] = transform_cls
    return mapping