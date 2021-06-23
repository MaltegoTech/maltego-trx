import logging
from typing import Any
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError, Element

from fastapi import FastAPI, Request
from starlette.responses import Response

from .maltego import MaltegoRequest, MaltegoResponse
from .registry import TransformRegistry

log = logging.getLogger("maltego.server")
logging.basicConfig(level=logging.DEBUG)

URL_TEMPLATE = '/run/<transform_name>/'
URL_TEMPLATE_NO_SLASH = '/run/<transform_name>'

app = FastAPI()
application = app  # application variable for usage with apache mod wsgi
registry: TransformRegistry = TransformRegistry("Maltego Technologies GmbH",
                                                "Maltego Technologies Gmbh",
                                                "This is an example", "localhost", ["demo"])


def get_exception_message(msg="An exception occurred with the transform. Check the logs for more details."):
    exception_response = MaltegoResponse()
    exception_response.exceptions = [msg]
    return ElementTree.tostring(exception_response.build_exceptions_xml())


def print_transforms():
    print("= Transform Server URLs =")
    for name, clazz in registry.transform_classes.items():
        print(URL_TEMPLATE.replace("<transform_name>", name) + ": " + clazz.__name__)
    print("\n")

    print("= Local Transform Names =")
    for name, clazz in registry.transform_classes.items():
        print(name + ": " + clazz.__name__)
    print("\n")


def run_transform(transform_name: str, client_msg: MaltegoRequest):
    transform_method = registry.transform_classes[transform_name.lower()]

    try:
        if hasattr(transform_method, "run_transform"):
            return transform_method.run_transform(client_msg)
        # else:
        #     return transform_method(client_msg)  # Transform method
    except Exception as e:
        log.error("An exception occurred while executing your transform code.")
        log.error(e, exc_info=True)
        return get_exception_message()


class XMLResponse(Response):
    media_type = "text/xml"

    def render(self, content: Any) -> bytes:
        if isinstance(content, Element):
            import lxml.etree as ET
            et = ET.fromstring(ElementTree.tostring(content))
            return ET.tostring(et, pretty_print=True, encoding='utf-8')
            # return ElementTree.tostring(content, encoding='utf-8')
        return content


@app.get('/')
def index():
    return "You have reached a Maltego Transform Server."


@app.post('/run/{transform_name}')
async def run_transforms(transform_name: str, request: Request):
    transform_name = transform_name.lower()
    if transform_name in registry.transform_classes:
        xml_data = await request.body()
        transform_method = registry.transform_classes[transform_name.lower()]

        try:
            maltego_message = MaltegoRequest.from_xml(xml_data)

            if hasattr(transform_method, "run_transform"):
                return await transform_method.run_transform(maltego_message)

        except ParseError:
            return XMLResponse(get_exception_message('Unprocessable XML'), 422)

        response_xml = await run_transform(transform_name, maltego_message)
        return ElementTree.tostring(response_xml)

    else:
        log.info("No transform found with the name '%s'." % transform_name)
        log.info("Available transforms are:\n %s" % str(list(registry.transform_classes.keys())))
        return "No transform found with the name '%s'." % transform_name, 404


@app.get('/run/{transform_name}')
async def x(transform_name: str):
    return f"Transform found with name '{transform_name}', you will need to send a POST request to run it."
