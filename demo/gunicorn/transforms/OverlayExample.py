from maltego_trx.maltego import MaltegoRequest, MaltegoResponse, CleanMaltegoEntity, EntityProperty, EntityOverlay
from maltego_trx.overlays import OverlayPosition, OverlayType

from maltego_trx.transform import DiscoverableTransform


class OverlayExample(DiscoverableTransform):
    """
    Returns a phrase with overlays on the graph.
    """

    @classmethod
    def create_entities(cls, request: MaltegoRequest, response: MaltegoResponse):
        person_name = request.value
        entity = CleanMaltegoEntity(entity_type='Phrase', value=f"Hi {person_name}, nice to meet you!")

        # Normally, when we create an overlay, we would reference a property name so that Maltego can then use the
        # value of that property to create the overlay. Sometimes that means creating a dynamic property, but usually
        # it's better to either use an existing property, or, if you created the Entity yourself, and only need the
        # property for the overlay, to use a hidden property. Here's an example of using a dynamic property:
        dynamic_icon_property = EntityProperty(name='dynamic_overlay_icon_name',
                                               display='Name for overlay image',
                                               value='Champion')
        dynamic_icon_property_overlay = EntityOverlay(property_name='dynamic_overlay_icon_name',
                                                      position=OverlayPosition.WEST,
                                                      overlay_type=OverlayType.IMAGE)

        # You *can* also directly supply the string value of the property, however this is not recommended. Why? If
        # the entity already has a property of the same ID (in this case, "DE"), then you would in fact be assigning the
        # value of that property, not the string "DE", which is not the intention. Nevertheless, here's an example:
        de_flag_overlay = EntityOverlay(property_name='DE',
                                        position=OverlayPosition.SOUTH_WEST,
                                        overlay_type=OverlayType.IMAGE)

        # Overlays can also be an additional field of text displayed on the entity:
        dynamic_property = EntityProperty('exampleDynamicPropertyName',
                                          'Example Dynamic Property',
                                          value='Maltego Overlay Testing',
                                          matching='loose')

        dynamic_property_overlay = EntityOverlay('exampleDynamicPropertyName',
                                                 OverlayPosition.NORTH,
                                                 OverlayType.TEXT)

        # Or a small color indicator
        color_overlay = EntityOverlay('#45e06f', OverlayPosition.NORTH_WEST, OverlayType.COLOUR)

        entity.add_properties(dynamic_icon_property, dynamic_property)
        entity.add_overlays(dynamic_icon_property_overlay, de_flag_overlay, dynamic_property_overlay, color_overlay)

        response.entities.append(entity)
