from extensions import registry
from maltego_trx.entities import Phrase
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

from maltego_trx.transform import DiscoverableTransform


@registry.register_transform(display_name="Greet Person", input_entity="maltego.Phrase",
                             description='Returns a Phrase greeting a Person on the Graph.',
                             output_entities=["maltego.Phrase"])
class GreetPerson(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        person_name = request.Value

        response.addEntity(Phrase, f"Hi {person_name}, nice to meet you!")
