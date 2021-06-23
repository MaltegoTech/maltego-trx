import sys

import transforms
from maltego_trx.handler import handle_run
from maltego_trx.server import app, registry

registry.author = 'John Doe'
registry.owner = 'Maltego Technologies GmbH'
registry.disclaimer = "This is a demo"
registry.host_url = 'http://localhost:8080'
registry.seed_ids = ['maltegotrx']

registry.scan_for_transforms(transforms)
registry.write_transforms_config()
registry.write_settings_config()

if __name__ == '__main__':
    handle_run(__name__, sys.argv + ['runserver'], app)
else:
    handle_run(__name__, sys.argv, app)
