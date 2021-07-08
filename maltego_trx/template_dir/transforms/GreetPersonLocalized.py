from maltego_trx.entities import Phrase
from maltego_trx.maltego import MaltegoTransform, MaltegoMsg
from maltego_trx.template_dir.extensions import registry
from maltego_trx.template_dir.settings import language_setting

from maltego_trx.transform import DiscoverableTransform


@registry.register_transform(display_name="Greet Person (localized)", input_entity="maltego.Phrase",
                             description='Returns a localized phrase greeting a person on the graph.',
                             settings=[language_setting],
                             output_entities=["maltego.Phrase"])
class GreetPersonLocalized(DiscoverableTransform):

    @classmethod
    def create_entities(cls, request: MaltegoMsg, response: MaltegoTransform):
        person_name = request.Value

        language: str = request.getTransformSetting(language_setting.id).lower()

        if language == 'af':
            greeting = f"Hallo {person_name}, lekker om jou te ontmoet!"
        elif language == "de":
            greeting = f"Moin {person_name}, schön dich kennen zu lernen!"
        else:
            greeting = f"Hello {person_name}, nice to meet you!"

        response.addEntity(Phrase, greeting)
