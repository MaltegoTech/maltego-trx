import socket
from libs.Maltego import MaltegoTransform, LINK_STYLES, BOOKMARK_CLRS, UIM_TYPES
from libs.entities import IPAddress, ASNumber


def dns_to_ip(request):
    """
    Receive DNS name from the client, and resolve to IP address.
    """
    response = MaltegoTransform()
    dns_name = request.Value

    try:
        ip_address = socket.gethostbyname(dns_name)
        response.addEntity(IPAddress, ip_address)
    except socket.error as e:
        response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])

    # Write the slider value as a UI message - just for fun
    response.addUIMessage("Slider value is at: " + str(request.Slider))

    return response.returnOutput()


def phrase_to_as(request):
    """
    Receive a phrase from the client, return as AS Numbers
    """
    response = MaltegoTransform()

    if not request.Value.isdigit():  # Ensure the input value is a digit
        response.addUIMessage("Input value '%s' is not a whole number." % request.Value, UIM_TYPES["partial"])
        return response.returnOutput()
    else:
        howmany = int(request.Value)

    is_div_str = request.getTransformSetting('ISDIV')  # You need ISDIV defined as a transform setting in the TDS
    if not is_div_str.isdigit():  # Ensure is_div setting is a digit
        response.addUIMessage("ISDIV setting value '%s' is not a whole number." % is_div_str, UIM_TYPES["partial"])
        return response.returnOutput()
    else:
        is_div = int(is_div_str)

    for i in range(1, howmany + 1):
        if i % is_div == 0:
            ent = response.addEntity(ASNumber, i)
            ent.setWeight(howmany - i)  # Set entity weight
            ent.addProperty('div', 'Divisible by', 'strict', is_div)  # Add a property

            # Change link and bookmark for odd and even numbers
            if i % 2 == 0:
                ent.setLinkColor('E8E8E8')
                ent.setNote('Even')
                ent.setLinkLabel('Even link')
                ent.setBookmark(BOOKMARK_CLRS["green"])
            else:
                ent.setLinkColor('ED8788')
                ent.setNote('Odd')
                ent.setLinkLabel('Odd link')
                ent.setLinkStyle(LINK_STYLES["dashed"])
                ent.setLinkThickness(2)
                ent.setBookmark(BOOKMARK_CLRS["red"])

        if i >= request.Slider:
            break

    return response.returnOutput()  # return the XML to the TDS server