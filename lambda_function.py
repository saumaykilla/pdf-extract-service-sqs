import json
import boto3
import os
from google import genai
from google.genai.types import Part
from dotenv import load_dotenv
import fitz
import requests

from models.ExtractResumeModel import Resume

load_dotenv()


s3_client = boto3.client('s3')

GRAPHQL_ENDPOINT = os.environ.get('GRAPHQL_ENDPOINT')
GRAPHQL_API_KEY = os.environ.get('GRAPHQL_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key=GEMINI_API_KEY)


def update_feedback(job_id: str, data: dict, status: str):
    """Update Feedback table via GraphQL mutation"""
    print(f"[i] Updating feedback for id: {job_id} with status: {status}")

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

def extract_text_with_links(pdf_path):
    doc = fitz.open(pdf_path)
    result = ""

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        result += f"\n--- Page {page_number} ---\n{text}\n"

        # Extract clickable hyperlinks
        for link in page.get_links():
            if "uri" in link:
                result += f"Link found: {link['uri']}\n"

    return result.strip()

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
    pdf_content = extract_text_with_links(local_path)

    # Gemini prompt
    prompt = f"""
    Extract the resume details from the given PDF content : {pdf_content}. 
    If a date field contains present/undefined, set it as null. 
    For descriptions and summary, set the string as HTML capturing styling and lists.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                prompt
            ],
            config={
                "response_mime_type": "application/json",
                "response_schema": Resume  # Pydantic model class
            }
        )
        result_data = json.loads(response.text)  # Convert Gemini response to dict
        print("[✓] Gemini processing successful")
        update_feedback(job_id, result_data, "success")
    except Exception as e:
        print(f"[✗] Gemini processing failed: {str(e)}")
        update_feedback(job_id, {}, "failed")