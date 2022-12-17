import os

from api import DISCOVERY_ENDPOINTS
from workflow import CSVWorkflow

API_KEY = os.environ["STARTUPRADAR_API_KEY"]

# set up default workflow
WORKFLOW = CSVWorkflow(DISCOVERY_ENDPOINTS, ".out/")
