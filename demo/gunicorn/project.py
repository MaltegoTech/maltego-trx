import sys
import transforms

from maltego_trx.registry import register_transform_classes
from maltego_trx.server import app
from maltego_trx.handler import handle_run

register_transform_classes(transforms)

handle_run(__name__, sys.argv, app)
