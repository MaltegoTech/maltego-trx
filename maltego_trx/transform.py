from maltego_trx.maltego import MaltegoTransform


class DiscoverableTransform:
    @classmethod
    def create_entities(cls, request, response):
        raise NotImplementedError("create_entities static method must be implemented in child class.")

    @classmethod
    def run_transform(cls, request):
        response = MaltegoTransform()
        cls.create_entities(request, response)
        return response.returnOutput()
