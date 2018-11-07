import logging
import transforms

from maltego_trx.registry import register_transform_function, register_transform_classes
from maltego_trx.server import get_server
from maltego_trx.maltego import VERSION

logging.basicConfig(level=logging.DEBUG)


# register_transform_function(transform_func)
register_transform_classes(transforms)


server = get_server()
app = server.app

if __name__ == '__main__':
    print("\n== Maltego Development Server: v%s ==\n" % VERSION)
    app.run(host="0.0.0.0", port=8080, debug=True)