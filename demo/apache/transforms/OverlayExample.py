from maltego_trx.entities import Phrase
from maltego_trx.overlays import Position, OverlayType

from maltego_trx.transform import DiscoverableTransform


class OverlayExample(DiscoverableTransform):
    """
    Returns a phrase with overlays on the graph.
    """

    @classmethod
    def create_entities(cls, request, response):
        person_name = request.Value
        entity = response.addEntity(Phrase, "Hi %s, nice to meet you!" % person_name)

        # references the icon name `Champion` and this is will show up as an overlay on the graph
        entity.addOverlay('Champion', Position.EAST, OverlayType.IMAGE)

        # addProperty(self, fieldName=None, displayName=None, matchingRule='loose', value=None):
        entity.addProperty("exampleDynamicPropertyName", "Example Dynamic Property", "loose", "Maltego Champion")

        # add the text of the property `exampleDynamicPropertyName` as an overlay
        entity.addOverlay('exampleDynamicPropertyName', Position.NORTH, OverlayType.TEXT)

        # add a color overlay
        entity.addOverlay('#45e06f', Position.NORTH_WEST, OverlayType.COLOUR)

        # add a flag overlay
        entity.addOverlay('DE', Position.SOUTH_WEST, OverlayType.IMAGE)
