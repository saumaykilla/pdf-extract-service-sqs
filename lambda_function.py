import json
import boto3
import os
from google import genai
from google.genai.types import Part
from dotenv import load_dotenv
import requests

from models.ExtractResumeModel import Resume

load_dotenv()


s3_client = boto3.client('s3')

GRAPHQL_ENDPOINT = os.environ.get('GRAPHQL_ENDPOINT')
GRAPHQL_API_KEY = os.environ.get('GRAPHQL_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key=GEMINI_API_KEY)


def update_feedback(job_id: str, data: dict, status: str):
    """Update FeedbackPolling table via GraphQL mutation"""
    mutation = """
    mutation UpdateFeedback($jobId: String!, $data: AWSJSON, $status: String!) {
      updateFeedbackPolling(input: {jobId: $jobId, data: $data, status: $status}) {
        jobId
        data
        status
      }
    }
    """
    variables = {
        "jobId": job_id,
        "data": json.dumps(data) if data else {},
        "status": status
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": GRAPHQL_API_KEY
    }
    response = requests.post(
        GRAPHQL_ENDPOINT,
        headers=headers,
        json={"query": mutation, "variables": variables}
    )
    if response.status_code != 200:
        raise Exception(f"GraphQL update failed: {response.text}")
    return response.json()
    

def lambda_handler(event, context):
    """Lambda entry point triggered by SQS"""
    # Expecting batch size 1 → only one message
    record = event["Records"][0]
    body = json.loads(record["body"])  # SQS message body

    # S3 event is inside body["Records"][0]
    s3_record = body["Records"][0]
    bucket = s3_record["s3"]["bucket"]["name"]
    key = s3_record["s3"]["object"]["key"]

    # Derive jobId from file name
    job_id = key.split("/")[-1].replace(".pdf", "")
    print(f"[i] Processing PDF: {key} → jobId: {job_id}")

    # Download PDF to /tmp
    local_path = f"/tmp/{key.split('/')[-1]}"
    try:
        s3_client.download_file(bucket, key, local_path)
        print(f"[✓] Downloaded {key} from bucket {bucket}")
    except Exception as e:
        print(f"[✗] S3 download failed: {str(e)}")
        update_feedback(job_id, {}, "failed")
        return

    # Read file content
    try:
        with open(local_path, "rb") as f:
            content = f.read()
        if not content:
            raise ValueError("File is empty")
    except Exception as e:
        print(f"[✗] Failed to read PDF: {str(e)}")
        update_feedback(job_id, {}, "failed")
        return

    # Gemini prompt
    prompt = """
    Extract the resume details from the given PDF. 
    If a date field contains present/undefined, set it as null. 
    For descriptions and summary, set the string as HTML capturing styling and lists.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                Part.from_bytes(data=content, mime_type="application/pdf"),
                prompt
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": Resume  # Pydantic model class
            }
        )
        result_data = response.to_dict()  # Convert Gemini response to dict
        print("[✓] Gemini processing successful")
        update_feedback(job_id, result_data, "success")
    except Exception as e:
        print(f"[✗] Gemini processing failed: {str(e)}")
        update_feedback(job_id, {}, "failed")