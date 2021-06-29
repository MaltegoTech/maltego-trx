from maltego_trx.entities import Phrase
from maltego_trx.maltego import MaltegoEntity
from maltego_trx.server import registry

from maltego_trx.transform import DiscoverableTransform


@registry.register(display_name="Greet Person", input_entity=Phrase, description="Greets a Person by the provided Name")
class GreetPerson(DiscoverableTransform):
    """
    returns a phrase greeting a person on the graph.
    """

    @classmethod
    def create_entities(cls, request, response):
        person_name = request.value

        response.entities.append(MaltegoEntity('Phrase', f"Hi {person_name}, nice to meet you!"))
