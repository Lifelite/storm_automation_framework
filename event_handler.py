import faust

app = faust.App('Storm', broker='kafka://localhost:29092')


class TestRequest(faust.Record):
    run_name: str
    run_id: int
    test_info: dict

class TestReponse(TestRequest):
    run_name: str
    run_id: int
    test_info: dict
    success: bool

@app.agent(value_type=TestRequest)
async def run_test(requests):
    async for request in requests:
        test_runner_handler(request)
