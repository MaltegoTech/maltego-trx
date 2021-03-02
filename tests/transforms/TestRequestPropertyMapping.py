from maltego_trx.entities import Phrase

from maltego_trx.transform import DiscoverableTransform


class TestRequestPropertyMapping(DiscoverableTransform):
    """
    Test if the automatic mapping of v2 propertyname `whois` -> `whois-info` has been done by the library. Original input
    contains only whois property name. see test_request.xml
    """

    @classmethod
    def create_entities(cls, request, response):
        v3_property_value = request.Properties['whois-info']
        response.addEntity(Phrase, "%s" % v3_property_value)
