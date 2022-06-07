import logging

from flask import Flask, request

from .maltego import MaltegoMsg, MaltegoTransform
from .registry import mapping

log = logging.getLogger("maltego.server")
logging.basicConfig(level=logging.DEBUG)

URL_TEMPLATE = '/run/<transform_name>/'
URL_TEMPLATE_NO_SLASH = '/run/<transform_name>'


def get_exception_message(msg="An exception occurred with the transform. Check the logs for more details."):
    transform_run = MaltegoTransform()
    transform_run.addUIMessage(msg, "PartialError")

    return transform_run.returnOutput()


def print_transforms():
    print("= Transform Server URLs =")
    for path in mapping:
        print(URL_TEMPLATE.replace("<transform_name>", path) + ": " + mapping[path].__name__)
    print("\n")

    print("= Local Transform Names =")
    for path in mapping:
        print(path + ": " + mapping[path].__name__)
    print("\n")


def run_transform(transform_name, client_msg):
    transform_method = mapping[transform_name]
    try:
        if hasattr(transform_method, "run_transform"):
            return transform_method.run_transform(client_msg), 200  # Transform class
        else:
            return transform_method(client_msg), 200  # Transform method
    except Exception as e:
        log.error("An exception occurred while executing your transform code.")
        log.error(e, exc_info=True)
        return get_exception_message(), 200


app = Flask(__name__)
application = app  # application variable for usage with apache mod wsgi


def transform_runner(transform_name):
    transform_name = transform_name.lower()
    if transform_name in mapping:
        if request.method == 'POST':
            client_msg = MaltegoMsg(request.data)
            return run_transform(transform_name, client_msg)
        else:
            return "Transform found with name '%s', you will need to send a POST request to run it." % transform_name, 200
    else:
        log.info("No transform found with the name '%s'." % transform_name)
        log.info("Available transforms are:\n %s" % str(list(mapping.keys())))
        return "No transform found with the name '%s'." % transform_name, 404


# Add the route with and without the slash, since POSTs can't be redirected
app.route(URL_TEMPLATE_NO_SLASH, methods=['GET', 'POST'])(transform_runner)
app.route(URL_TEMPLATE, methods=['GET', 'POST'])(transform_runner)


@app.route('/', methods=['GET', 'POST'])
def index():
    return "You have reached a Maltego Transform Server.", 200
