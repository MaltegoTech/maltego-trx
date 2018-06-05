import traceback
import logging

from flask import Flask, request
from libs.discovery import get_transforms
from libs.Maltego import MaltegoMsg

from legacy_example import dns_to_ip, phrase_to_as

log = logging.getLogger("maltego.server")
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
debug = True

discovered_transforms = get_transforms()
manually_added_transforms = {
    # Dict in format "transform_name": "transform method"
    "dns-to-ip": dns_to_ip,
    "phrase-to-as": phrase_to_as,
}

# Combine two sets of transforms
all_transforms = discovered_transforms.copy()
all_transforms.update(manually_added_transforms)


def run_transform(transform_name, request_body):
    try:
        client_msg = MaltegoMsg(request_body)
        transform_method = all_transforms[transform_name]
        return transform_method(client_msg), 200
    except Exception as e:
        log.error("An exception occurred while executing your transform code.")
        log.error(e, exc_info=True)


@app.route('/run/<transform_name>/', methods=['GET', 'POST'])
def transform_runner(transform_name):
    if transform_name in all_transforms:
        if request.method == 'POST':
            return run_transform(transform_name, request.body)
        else:
            return "Transform found with name '%s', you will need to send a POST request to run it." % transform_name, 200
    else:
        log.info("No transform found with the name '%s'." % transform_name )
        log.info("Available transforms are:\n %s" % str(list(all_transforms.keys())))
        return "No transform found with the name '%s'." % transform_name, 404


@app.route('/', methods=['GET', 'POST'])
def index():
    return "You have reached a Maltego Transform Server.", 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)