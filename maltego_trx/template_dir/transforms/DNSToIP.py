import socket

from extensions import registry
from maltego_trx.entities import IPAddress
from maltego_trx.maltego import UIM_TYPES, MaltegoMsg, MaltegoTransform
from maltego_trx.transform import DiscoverableTransform


@registry.register_transform(display_name="DNS to IP", input_entity="maltego.DNSName",
                             description='Receive DNS name from the Client, and resolve to IP address.',
                             output_entities=["maltego.IPv4Address"])
class DNSToIP(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        dns_name = request.Value

        try:
            ip_address = socket.gethostbyname(dns_name)
            response.addEntity(IPAddress, ip_address)
        except socket.error as e:
            response.addUIMessage(f"Error: {e}", UIM_TYPES["partial"])

        # Write the slider value as a UI message - just for fun
        response.addUIMessage(f"Slider value is at: {request.Slider}")
