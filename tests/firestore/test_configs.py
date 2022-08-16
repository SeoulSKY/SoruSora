import asyncio
import pytest

from firestore import configs


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()

    yield loop

    pending = asyncio.tasks.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
    loop.run_until_complete(asyncio.sleep(1))

    loop.close()


class TestConfigs:

    def setup_method(self, test_method):
        from firestore import db
        self.collection = db.collection("configs")
        self.user_id = 777

    async def teardown_method(self, test_method):
        async for doc in self.collection.stream():
            await doc.reference.delete()

    async def test_have(self):
        assert await configs.have(self.user_id) == (await self.collection.document(str(self.user_id)).get()).exists

        async for doc in self.collection.stream():
            doc.reference.delete()

        assert await configs.have(self.user_id) == (await self.collection.document(str(self.user_id)).get()).exists

    async def test_get(self):
        config = configs.Config(self.user_id)

        assert (await configs.get(self.user_id)).to_dict() == config.to_dict()

        config.translate_to = ["en"]
        await self.collection.document(str(self.user_id)).set(config.to_dict())

        assert (await configs.get(self.user_id)).to_dict() == config.to_dict()

    async def test_set(self):
        config = configs.Config(self.user_id, translate_to=["ko"])

        await configs.set(config)
        assert (await self.collection.document(str(self.user_id)).get()).to_dict() == config.to_dict()


if __name__ == "__main__":
    pytest.main()
