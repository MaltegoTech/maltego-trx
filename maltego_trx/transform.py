from maltego_trx.maltego import MaltegoTransform


class DiscoverableTransform:
    @classmethod
    def create_entities(cls, request, response):
        raise NotImplementedError("create_entities static method must be implemented in child class.")

    @classmethod
    def run_transform(cls, request):
        response = cls.create_entities(request, MaltegoTransform())
        return response.returnOutput()
