from maltego_trx.registry import register_transform_classes
from maltego_trx.server import app
from tests import transforms


def test_request_property_mapping():
    register_transform_classes(transforms)
    app.testing = True

    with app.test_client() as test_app:
        response = make_transform_call(test_app, "/run/testrequestpropertymapping/")
        assert response.status_code == 200
        data = response.data.decode('utf8')
        assert "whois-info found" in data


def make_transform_call(test_app=None, run_endpoint=""):
    with open('test_request.xml') as requestMsg:
        response = test_app.post(run_endpoint, data=requestMsg.read())
    return response
