import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TRACKER_TOKEN_N")
API_KEY_G = os.getenv("TRACKER_TOKEN_G")

class Config:
    TRACKER_API_URL = "https://api.tracker.yandex.net/v3"
    OAUTH_TOKEN = API_KEY
    OAUTH_TOKEN_G = API_KEY_G
    ORG_ID = "bpfrvf6d7hoa6l9fforp"
    TEST_ISSUE_ID = "TESTN-1"
    QUEUE_KEY = "TESTN"
    INVALID_TOKEN = "invalid_token_123"
    INVALID_ISSUE_ID = "INVALID-123"
    READ_ONLY_TOKEN = "your_read_only_token_here"
    QUEUE_LEAD = "sm-nastya2505"
    TESTN_PROJECT_ID = "2"