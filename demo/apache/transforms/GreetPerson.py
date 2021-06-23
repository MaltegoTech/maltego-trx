from maltego_trx.maltego import CleanMaltegoEntity

from maltego_trx.transform import DiscoverableTransform


class GreetPerson(DiscoverableTransform):
    """
    Returns a phrase greeting a person on the graph.
    """

    @classmethod
    def create_entities(cls, request, response):
        person_name = request.value

        response.entities.append(CleanMaltegoEntity('Phrase', f"Hi {person_name}, nice to meet you!"))
