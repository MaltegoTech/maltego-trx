from abc import abstractmethod

from maltego_trx.maltego import MaltegoRequest, MaltegoResponse


class DiscoverableTransform:
    @classmethod
    @abstractmethod
    async def create_entities(cls, request: MaltegoRequest, response: MaltegoResponse):
        raise NotImplementedError("create_entities static method must be implemented in child class.")

    @classmethod
    async def run_transform(cls, request: MaltegoRequest):
        response = MaltegoResponse()
        await cls.create_entities(request, response)
        return response.build_xml()
