import os
import json
from google.cloud import storage
from google.api_core import exceptions as google_exceptions

PROJECT_ID = "ai-incubation-team"
BUCKET_NAME = "benchhub-artifacts"
REGISTRY_PATH = "configs/registry.json"

def test_fetch():
    print(f"Testing fetch from gs://{BUCKET_NAME}/{REGISTRY_PATH} using project {PROJECT_ID}")
    client = storage.Client(project=PROJECT_ID)
    try:
        bucket = client.bucket(BUCKET_NAME, user_project=PROJECT_ID)
        blob = bucket.blob(REGISTRY_PATH)
        
        print(f"Blob name: {blob.name}")
        print(f"Bucket name: {blob.bucket.name}")
        print(f"Bucket user_project: {blob.bucket.user_project}")
        
        # This is where the URL is generated and called
        content = blob.download_as_text()
        print("Successfully downloaded registry content.")
        print(f"Content length: {len(content)}")
    except Exception as e:
        print(f"Caught exception: {e}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code}")
            # print(f"Response text: {e.response.text}")

if __name__ == "__main__":
    test_fetch()
