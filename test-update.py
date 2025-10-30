import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT")  # e.g. https://xxxx.appsync-api.us-east-1.amazonaws.com/graphql
GRAPHQL_API_KEY = os.getenv("GRAPHQL_API_KEY")    # your AppSync API key

def update_feedback(job_id: str, data: dict, status: str):
    """Update Feedback table via GraphQL mutation"""
    print(f"[i] Updating feedback for jobId: {job_id} with status: {status}")

    mutation = """
    mutation  updateFeedbackPolling($input: UpdateFeedbackPollingInput!) {
      updateFeedbackPolling(input: $input) {
        id
        data
        status
      }
    }
    """

    variables = {
        "input": {
            "id": job_id,
            "data": json.dumps(data) if data else "{}",
            "status": status
        }
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": GRAPHQL_API_KEY
    }

    try:
        response = requests.post(
            GRAPHQL_ENDPOINT,
            headers=headers,
            json={"query": mutation, "variables": variables}
        )
        if response.status_code != 200:
            print(f"[✗] GraphQL request failed: {response.status_code}")
            print(response.text)
            return "failed"

        res_json = response.json()
        print("[✓] Feedback updated successfully:", res_json)
        return "completed"
    except Exception as e:
        print(f"[✗] GraphQL update failed: {str(e)}")
        return "failed"


if __name__ == "__main__":
    update_feedback("031HOA8iXhqwKoxZV-36V", {"text": "Extracted content"}, "success")