import asyncio

import faust

from test_runner_utils import handle_test_request

app = faust.App('Storm', broker='kafka://localhost:29092')


class TestRequest(faust.Record):
    run_name: str
    run_id: int
    test_params: dict

class TestResponse(TestRequest):
    run_name: str
    run_id: int
    test_params: dict
    success: bool

test_request_topic = topic = app.topic("test.request", value_type=TestRequest)

@app.agent(test_request_topic)
async def run_test(requests):
    async for request in requests:
        await handle_test_request(
            request.run_name,
            request.run_id,
            request.test_params
        )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.start())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting down Faust worker...")
    finally:
        loop.run_until_complete(app.stop())
