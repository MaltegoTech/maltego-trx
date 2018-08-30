import socket
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.entities import IPAddress

from maltego_trx.transform import DiscoverableTransform


class DNSToIP(DiscoverableTransform):
    """
    Receive DNS name from the client, and resolve to IP address.
    """

    @classmethod
    def create_entities(cls, request, response):
        dns_name = request.Value

        try:
            ip_address = socket.gethostbyname(dns_name)
            response.addEntity(IPAddress, ip_address)
        except socket.error as e:
            response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])

        # Write the slider value as a UI message - just for fun
        response.addUIMessage("Slider value is at: " + str(request.Slider))
