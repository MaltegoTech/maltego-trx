import logging

from flask import Flask, request
from maltego_trx.maltego import MaltegoMsg
from .registry import transform_classes, transform_functions
from .utils import name_to_path

log = logging.getLogger("maltego.server")
logging.basicConfig(level=logging.DEBUG)


URL_TEMPLATE = '/run/<transform_name>/'
EXCEPTION_MESSAGE = """<MaltegoMessage>
    <MaltegoTransformResponseMessage>
        <Entities>
        </Entities>
        <UIMessages>
            <UIMessage MessageType='PartialError'>
                An exception occurred with the transform. Check the logs for more details.
            </UIMessage>
        </UIMessages>
    </MaltegoTransformResponseMessage>
</MaltegoMessage>"""


class TransformServer:
    def __init__(self, trans_functions, trans_classes):
        self.transform_functions = trans_functions
        self.transform_classes = trans_classes
        self.mapping = self.get_url_mapping()
        self.print_transforms()

        self.app = self.get_app()

    def get_url_mapping(self):
        # Get mapping from URL path to transform
        mapping = {}
        for transform in self.transform_functions + self.transform_classes:
            url_path = name_to_path(transform.__name__)
            mapping[url_path] = transform
        return mapping

    def get_app(self):
        app = Flask(__name__)

        @app.route(URL_TEMPLATE, methods=['GET', 'POST'])
        def transform_runner(transform_name):
            transform_name = transform_name.lower()
            if transform_name in self.mapping:
                if request.method == 'POST':
                    transform_val = self.mapping[transform_name]
                    return run_transform(transform_val, request.data)
                else:
                    return "Transform found with name '%s', you will need to send a POST request to run it." % transform_name, 200
            else:
                log.info("No transform found with the name '%s'." % transform_name)
                log.info("Available transforms are:\n %s" % str(list(self.mapping.keys())))
                return "No transform found with the name '%s'." % transform_name, 404

        @app.route('/', methods=['GET', 'POST'])
        def index():
            return "You have reached a Maltego Transform Server.", 200

        return app

    def print_transforms(self):
        print("\n\n === SERVER TRANSFORM PATHS ===")
        for path in self.mapping:
            print(URL_TEMPLATE.replace("<transform_name>", path) + ": " + self.mapping[path].__name__)
        print("\n")


def run_transform(transform_method, request_body):
    try:
        client_msg = MaltegoMsg(request_body)
        if hasattr(transform_method, "run_transform"):
            return transform_method.run_transform(client_msg), 200  # Transform class
        else:
            return transform_method(client_msg), 200  # Transform method
    except Exception as e:
        log.error("An exception occurred while executing your transform code.")
        log.error(e, exc_info=True)
        return EXCEPTION_MESSAGE, 200


def get_server():
    return TransformServer(transform_functions, transform_classes)
