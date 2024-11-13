from os import getenv

import requests

QASE_API_KEY = getenv('QASE_API_KEY')
def make_bulk_api_post(payload, project_id, run_id, api_key):

    key = api_key or QASE_API_KEY

    url = f"https://api.qase.io/v1/result/{project_id}/{run_id}/bulk"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Token": key
    }
    response = None
    try:
        response = requests.post(url, json=payload, headers=headers)
    except requests.exceptions as e:
        print(f"An error occurred when submitting test results: {e}")

    if response.text != '{"status":true}':
        print(f"An error occurred when submitting test results: {response.text}")


def submit_bulk_test_results(
        project_id: str,
        run_id: int,
        api_key: str,
        result_array: [dict]
):
    payload = {
        "results": result_array
    }
    make_bulk_api_post(payload, project_id, run_id, api_key)

if __name__ == "__main__":
    pass
