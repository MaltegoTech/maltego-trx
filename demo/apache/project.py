import sys

import transforms
from maltego_trx.handler import handle_run
from maltego_trx.legacy_registry import register_transform_classes
from maltego_trx.server import app

# register_transform_function(transform_func)
register_transform_classes(transforms)

handle_run(__name__, sys.argv, app)
