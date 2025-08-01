from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.credentials import Credentials

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("IBM_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")

BASE_URL = f"https://{REGION}.ml.cloud.ibm.com"

# Set up credentials
credentials = Credentials(api_key=API_KEY, url=BASE_URL)

# Initialize and return model object
def get_granite_model():
    return ModelInference(
        model_id="ibm/granite-13b-instruct-v2",
        credentials=credentials,
        project_id=PROJECT_ID
    )  